"""
conditions.py — the five experimental conditions for the AIL+MoIE benchmark.

Conditions (per pre-registration, Section 9):
  C1  baseline few-shot
  C2  chain-of-thought
  C3  tree-of-thoughts
  C4  AIL+MoIE, internal knowledge only
  C5  AIL+MoIE + retrieval-backed anomaly search

All conditions share a base model. Token usage is recorded per call so that
harness.py can build the compute-matched comparison.

No API key is embedded. Set ANTHROPIC_API_KEY in the environment.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Callable

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "ollama:latest")
OLLAMA_GENERATE_PATH = "/api/generate"
OLLAMA_CHAT_PATH = "/api/chat"
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")


# --------------------------------------------------------------------------
# client
# --------------------------------------------------------------------------

@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens,
        )


@dataclass
class Reply:
    text: str
    usage: Usage


class ModelClient:
    """Thin LLM client with backend auto-selection.

    Priority:
      1. If OLLAMA_BASE_URL is set or a local Ollama server is reachable, use Ollama.
      2. Otherwise fall back to Anthropic Messages API.
    Token usage is recorded on every call.
    """

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        temperature: float = 1.0,
        max_tokens: int = 2000,
        max_retries: int = 5,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.call_log: list[dict] = []
        self._backend: str | None = None

        # Determine backend
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        explicit_ollama = os.environ.get("OLLAMA_MODEL") not in (None, "")
        use_ollama = explicit_ollama or (
            deepseek_key is None
            and self._ollama_reachable(ollama_url)
        )

        if use_ollama:
            self._backend = "ollama"
            self.ollama_base = ollama_url.rstrip("/")
            self.ollama_model = os.environ.get("OLLAMA_MODEL", self.model)
            self.api_key = None
        elif deepseek_key:
            self._backend = "deepseek"
            self.deepseek_api_key = deepseek_key
            self.deepseek_model = os.environ.get("DEEPSEEK_MODEL", DEEPSEEK_MODEL)
            self.api_key = None
        elif api_key:
            self._backend = "anthropic"
            self.api_key = api_key
            if not model.startswith("claude"):
                raise RuntimeError(
                    "Anthropic backend requires a Claude model name. "
                    f"Got: {model!r}. Pass --model claude-3-5-sonnet-20240620 or set OLLAMA_MODEL."
                )
        else:
            raise RuntimeError(
                "No LLM backend available. Set ANTHROPIC_API_KEY for Anthropic, "
                "DEEPSEEK_API_KEY for DeepSeek, "
                "or start a local Ollama server and optionally set OLLAMA_MODEL."
            )

    @staticmethod
    def _ollama_reachable(base_url: str, timeout: float = 1.0) -> bool:
        try:
            req = urllib.request.Request(f"{base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False

    def __call__(self, prompt: str, system: str | None = None,
                 temperature: float | None = None) -> Reply:
        if self._backend == "ollama":
            return self._call_ollama(prompt, system, temperature)
        if self._backend == "deepseek":
            return self._call_deepseek(prompt, system, temperature)
        return self._call_anthropic(prompt, system, temperature)

    def _call_anthropic(self, prompt: str, system: str | None = None,
                        temperature: float | None = None) -> Reply:
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature if temperature is None else temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        req = urllib.request.Request(
            API_URL,
            data=json.dumps(body).encode(),
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": API_VERSION,
            },
            method="POST",
        )

        delay = 2.0
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=180) as resp:
                    data = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503, 529) or attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2
            except urllib.error.URLError:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2

        text = "\n".join(
            b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
        )
        u = data.get("usage", {})
        usage = Usage(u.get("input_tokens", 0), u.get("output_tokens", 0))
        self.call_log.append({"tokens": usage.total, "model": self.model, "backend": "anthropic"})
        return Reply(text, usage)

    def _call_ollama(self, prompt: str, system: str | None = None,
                     temperature: float | None = None) -> Reply:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature if temperature is None else temperature,
                "num_predict": self.max_tokens,
            },
        }

        url = f"{self.ollama_base}{OLLAMA_CHAT_PATH}"
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers={"content-type": "application/json"}, method="POST")

        delay = 2.0
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=300) as resp:
                    result = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503) or attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2
            except urllib.error.URLError:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2

        text = result.get("message", {}).get("content", "")
        eval_count = result.get("eval_count", 0)
        prompt_eval_count = result.get("prompt_eval_count", 0)
        usage = Usage(prompt_eval_count, eval_count)
        self.call_log.append({"tokens": usage.total, "model": self.ollama_model, "backend": "ollama"})
        return Reply(text, usage)

    def _call_deepseek(self, prompt: str, system: str | None = None,
                       temperature: float | None = None) -> Reply:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": self.deepseek_model,
            "messages": messages,
            "stream": False,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens,
        }

        url = DEEPSEEK_API_URL
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "content-type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}",
            },
            method="POST",
        )

        delay = 2.0
        for attempt in range(self.max_retries):
            try:
                with urllib.request.urlopen(req, timeout=300) as resp:
                    result = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                if e.code not in (429, 500, 502, 503) or attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2
            except urllib.error.URLError:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 2

        text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage_data = result.get("usage", {})
        usage = Usage(
            usage_data.get("prompt_tokens", 0),
            usage_data.get("completion_tokens", 0),
        )
        self.call_log.append({"tokens": usage.total, "model": self.deepseek_model, "backend": "deepseek"})
        return Reply(text, usage)


# --------------------------------------------------------------------------
# shared output contract
# --------------------------------------------------------------------------

OUTPUT_CONTRACT = """
Your response must end with a section headed exactly:

## FALSIFIABLE PREDICTIONS

listing at least 3 numbered predictions. Each prediction must state:
  (a) the measurable outcome,
  (b) the dataset or measurement procedure that would test it,
  (c) a time horizon,
  (d) what observation would falsify it.
""".strip()


@dataclass
class Run:
    condition: str
    question_id: str
    question: str
    output: str
    usage: Usage
    n_samples: int = 1
    transcript: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["usage"] = {"input": self.usage.input_tokens,
                      "output": self.usage.output_tokens,
                      "total": self.usage.total}
        return d


# --------------------------------------------------------------------------
# C1 — baseline few-shot
# --------------------------------------------------------------------------

C1_SYSTEM = "You are a research scientist generating hypotheses for open scientific questions."

C1_PROMPT = """Generate a novel, testable hypothesis addressing the following open scientific question.

QUESTION: {question}

{contract}
"""


def run_c1(client: ModelClient, qid: str, question: str) -> Run:
    r = client(C1_PROMPT.format(question=question, contract=OUTPUT_CONTRACT),
               system=C1_SYSTEM)
    return Run("C1", qid, question, r.text, r.usage,
               transcript=[{"role": "single_pass", "text": r.text}])


# --------------------------------------------------------------------------
# C2 — chain of thought
# --------------------------------------------------------------------------

C2_PROMPT = """Generate a novel, testable hypothesis addressing the following open scientific question.

QUESTION: {question}

Think step by step. Work through the problem explicitly before committing to a hypothesis:
what is known, what is contested, what mechanisms could account for the phenomenon, and
which of those mechanisms is most likely to yield a testable claim.

{contract}
"""


def run_c2(client: ModelClient, qid: str, question: str) -> Run:
    r = client(C2_PROMPT.format(question=question, contract=OUTPUT_CONTRACT),
               system=C1_SYSTEM)
    return Run("C2", qid, question, r.text, r.usage,
               transcript=[{"role": "cot", "text": r.text}])


# --------------------------------------------------------------------------
# C3 — tree of thoughts
# --------------------------------------------------------------------------

C3_BRANCH = """Open scientific question: {question}

Propose {k} substantively DIFFERENT high-level approaches to generating a novel hypothesis
here. The approaches should differ in the mechanism or level of description they invoke,
not merely in wording. Number them 1..{k}. Two or three sentences each."""

C3_EVAL = """Open scientific question: {question}

Candidate approaches:
{branches}

Evaluate each approach for its likelihood of yielding a novel AND testable hypothesis.
Then state which single approach is most promising, as: BEST: <number>"""

C3_EXPAND = """Open scientific question: {question}

Pursue this approach fully and develop it into a specific hypothesis:
{chosen}

{contract}
"""


def run_c3(client: ModelClient, qid: str, question: str, k: int = 4) -> Run:
    usage = Usage()
    tr = []

    r1 = client(C3_BRANCH.format(question=question, k=k), system=C1_SYSTEM)
    usage += r1.usage
    tr.append({"role": "branch", "text": r1.text})

    r2 = client(C3_EVAL.format(question=question, branches=r1.text), system=C1_SYSTEM)
    usage += r2.usage
    tr.append({"role": "evaluate", "text": r2.text})

    chosen = r2.text
    r3 = client(C3_EXPAND.format(question=question, chosen=chosen,
                                 contract=OUTPUT_CONTRACT), system=C1_SYSTEM)
    usage += r3.usage
    tr.append({"role": "expand", "text": r3.text})

    return Run("C3", qid, question, r3.text, usage, transcript=tr)


# --------------------------------------------------------------------------
# C4 / C5 — AIL + MoIE
# --------------------------------------------------------------------------

CRITIC_SYSTEM = """You are the Inversion Critic in a Mixture of Inversion Experts system.
Your function is to surface the hidden assumptions framing a question and invert the most
load-bearing one. You steelman an assumption before inverting it. You do not soften
inversions into hedged restatements of consensus. Your core question is:
"What if the opposite is true?" """

SCOUT_SYSTEM = """You are the Positive Deviant Scout in a Mixture of Inversion Experts system.
You search for real-world cases, anomalies, historical episodes and failed predictions that
FIT an inverted claim, and — mandatorily — cases that CONTRADICT it. Reporting disconfirming
evidence is not optional; an inversion with no boundary is not a finding. Your core question:
"Where has this inversion succeeded or failed in practice?" """

SYNTH_SYSTEM = """You are the Mechanism Synthesizer in a Mixture of Inversion Experts system.
You build a unified causal model from the tension between Critic and Scout, specify the
boundary conditions separating the regime where the original assumption holds from the regime
where the inversion holds, and surface your own new assumptions for further inversion.
Your core question: "What coherent framework explains both views?" """

STEP1_EXTRACT = """QUESTION: {question}

Step 1 — ASSUMPTION EXTRACTION.
List the explicit and implicit assumptions embedded in this question. For each, state it in
its strongest, most defensible form (steelman it).

Step 2 — ASSUMPTION RANKING.
For each assumption rate, on 0-1 scales:
  Centrality  (how much of the field's framing rests on it)
  Consensus   (how widely it is accepted without argument)
  Testability (how readily it is empirically checked)
Compute Priority = Centrality x Consensus x (1 - Testability).
Report the table, then state: SELECTED ASSUMPTION: <the highest-priority assumption>"""

STEP2_INVERT = """QUESTION: {question}

SELECTED ASSUMPTION (from step 2):
{selected}

Step 3 — INVERSION.
Invert the selected assumption. State the inversion as a POSITIVE CLAIM with a proposed
mechanism, not as a bare negation.

Step 4 — ENABLING CONDITIONS.
Under what conditions would the inverted claim hold? Specify the boundary: assumption holds
in regime R1, inversion holds in regime R2. What separates them?

Also identify MISSING VARIABLES: factors invisible in the original framing but load-bearing
in the inverted world."""

STEP3_SCOUT = """QUESTION: {question}

INVERTED CLAIM AND CONDITIONS:
{inversion}

Step 5 — ANOMALY DISCOVERY.
(a) Find empirical anomalies, historical cases, and failed predictions of the ORIGINAL
    framing that are consistent with the inverted claim.
(b) MANDATORY: find cases that CONTRADICT the inverted claim. Report them plainly.
(c) From (a) and (b), sharpen the boundary condition.

{retrieval_note}"""

STEP4_SYNTH = """QUESTION: {question}

INVERSION: {inversion}

SCOUT FINDINGS: {anomalies}

Step 6 — CAUSAL MECHANISM CONSTRUCTION.
Build a causal model linking the inverted claim to observable consequences. Incorporate the
supporting anomalies as evidence and the contradicting cases as boundary conditions.
State any NEW ASSUMPTIONS your model itself introduces.

Step 7 — NEW PRIMITIVE.
Derive a concept, construct or metric that the original framing could not have generated."""

STEP5_CRITIQUE = """QUESTION: {question}

PROPOSED MODEL:
{model}

Step 7 (second pass) — ADVERSARIAL CRITIQUE.
Attack this model. Identify: residual unexamined assumptions; the conditions under which the
ORIGINAL assumption still holds; the weakest link in the causal chain; and what evidence
would most efficiently kill the model."""

STEP6_UIM = """QUESTION: {question}

INVERSION: {inversion}
SCOUT FINDINGS: {anomalies}
CAUSAL MODEL: {model}
CRITIQUE: {critique}

Step 8 — UNIFIED INVERSION MODEL.
Produce the final output: the core inverted axiom, boundary conditions, causal architecture,
new measurable constructs, and the falsifiable predictions. Address the critique directly —
do not ignore it.

{contract}
"""

RETRIEVAL_ON = """You have web search available. Use it to ground the anomalies in real,
citable cases. Prefer primary sources. Report what you actually found, including when a
search fails to support the inverted claim."""

RETRIEVAL_OFF = """Use internal knowledge only. Do not fabricate citations: if you are
uncertain whether a case is real, say so explicitly and mark it as unverified."""


def _run_moie(client: ModelClient, qid: str, question: str,
              condition: str, retrieval: bool) -> Run:
    usage = Usage()
    tr = []

    def step(prompt, system, label):
        nonlocal usage
        r = client(prompt, system=system)
        usage += r.usage
        tr.append({"role": label, "text": r.text})
        return r.text

    extracted = step(STEP1_EXTRACT.format(question=question),
                     CRITIC_SYSTEM, "critic:extract+rank")

    inversion = step(STEP2_INVERT.format(question=question, selected=extracted),
                     CRITIC_SYSTEM, "critic:invert+conditions")

    anomalies = step(STEP3_SCOUT.format(
                        question=question, inversion=inversion,
                        retrieval_note=RETRIEVAL_ON if retrieval else RETRIEVAL_OFF),
                     SCOUT_SYSTEM, "scout:anomalies")

    model = step(STEP4_SYNTH.format(question=question, inversion=inversion,
                                    anomalies=anomalies),
                 SYNTH_SYSTEM, "synth:causal+primitive")

    critique = step(STEP5_CRITIQUE.format(question=question, model=model),
                    CRITIC_SYSTEM, "critic:adversarial")

    uim = step(STEP6_UIM.format(question=question, inversion=inversion,
                                anomalies=anomalies, model=model,
                                critique=critique, contract=OUTPUT_CONTRACT),
               SYNTH_SYSTEM, "synth:uim")

    return Run(condition, qid, question, uim, usage, transcript=tr)


def run_c4(client: ModelClient, qid: str, question: str) -> Run:
    return _run_moie(client, qid, question, "C4", retrieval=False)


def run_c5(client: ModelClient, qid: str, question: str) -> Run:
    return _run_moie(client, qid, question, "C5", retrieval=True)


# --------------------------------------------------------------------------
# best-of-n selection, for the compute-matched arm
# --------------------------------------------------------------------------

SELECTOR_SYSTEM = """You select the single best hypothesis from a set of candidates.
You are not the judge who scores final outputs; you are a selection step internal to a
baseline condition."""

SELECTOR_PROMPT = """Open scientific question: {question}

{candidates}

Select the single candidate that is most NOVEL (semantically distant from standard textbook
answers) while remaining coherent and testable. Respond with exactly: BEST: <number>
and one sentence of justification."""


def best_of_n(client: ModelClient, qid: str, question: str,
              base_fn: Callable, n: int, condition_suffix: str = "-bon") -> Run:
    """Run a baseline condition n times and select the best candidate.

    Selector token cost is charged to the baseline's budget. This is deliberately
    conservative AGAINST the MoIE hypothesis: the baseline arm gets its full
    generation budget and the selection overhead is counted as baseline compute,
    so a MoIE win cannot be attributed to the baseline being under-resourced.
    """
    runs = [base_fn(client, qid, question) for _ in range(n)]
    usage = Usage()
    for r in runs:
        usage += r.usage

    if n == 1:
        chosen = runs[0]
        chosen.condition += condition_suffix
        chosen.n_samples = 1
        return chosen

    blocks = "\n\n".join(
        f"--- CANDIDATE {i+1} ---\n{r.output}" for i, r in enumerate(runs)
    )
    sel = client(SELECTOR_PROMPT.format(question=question, candidates=blocks),
                 system=SELECTOR_SYSTEM, temperature=0.0)
    usage += sel.usage

    idx = 0
    for token in sel.text.split():
        digits = "".join(ch for ch in token if ch.isdigit())
        if digits:
            idx = min(max(int(digits) - 1, 0), n - 1)
            break

    winner = runs[idx]
    return Run(
        condition=runs[0].condition + condition_suffix,
        question_id=qid,
        question=question,
        output=winner.output,
        usage=usage,
        n_samples=n,
        transcript=[{"role": "selector", "text": sel.text},
                    {"role": "winner_index", "text": str(idx)}],
    )


CONDITIONS = {
    "C1": run_c1,
    "C2": run_c2,
    "C3": run_c3,
    "C4": run_c4,
    "C5": run_c5,
}

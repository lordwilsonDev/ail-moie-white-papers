"""MMVP CLI: L0/L1 verify + L2/L3 mission runner."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _mission_path(mission_id: str) -> Path:
    return ROOT / "missions" / f"{mission_id}.md"


def _load_mission(mission_id: str) -> dict:
    path = _mission_path(mission_id)
    if not path.exists():
        raise SystemExit(f"Mission not found: {path}")
    text = path.read_text(encoding="utf-8")
    frontmatter = {}
    body = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            import yaml

            frontmatter = yaml.safe_load(text[3:end]) or {}
            body = text[end + 3 :].strip()
    return {
        "id": frontmatter.get("id", mission_id),
        "title": frontmatter.get("title", mission_id),
        "providers": frontmatter.get("providers", []),
        "questions": frontmatter.get("questions", []),
        "objective": frontmatter.get("objective", ""),
        "raw": body,
    }


def _build_backends(providers: list[str]):
    backends = []
    available = []
    for name in providers:
        if name == "mock":
            from adapters.mock_adapter import MockAdapter

            backends.append(MockAdapter())
            available.append("mock")
            continue
        env_key = f"{name.upper()}_API_KEY"
        url_key = f"{name.upper()}_BASE_URL"
        api_key = os.getenv(env_key)
        base_url = os.getenv(url_key)
        if not api_key and name not in {"ollama"}:
            print(f"WARN: {env_key} not set; skipping {name}")
            continue
        if name == "openai":
            from adapters.openai_adapter import OpenAIAdapter

            backends.append(OpenAIAdapter(api_key=api_key or ""))
        elif name == "anthropic":
            from adapters.anthropic_adapter import AnthropicAdapter

            backends.append(AnthropicAdapter(api_key=api_key or ""))
        elif name == "deepseek":
            from adapters.deepseek_adapter import DeepSeekAdapter

            backends.append(DeepSeekAdapter(api_key=api_key or ""))
        elif name == "ollama":
            from adapters.ollama_adapter import OllamaAdapter

            backends.append(OllamaAdapter(api_key=api_key or "", base_url=base_url or "http://localhost:11434"))
        elif name == "google":
            from adapters.google_adapter import GoogleAdapter

            backends.append(GoogleAdapter(api_key=api_key or ""))
        elif name == "huggingface":
            from adapters.huggingface_adapter import HuggingFaceAdapter

            backends.append(HuggingFaceAdapter(api_key=api_key or ""))
        else:
            print(f"WARN: unsupported provider {name}; skipping")
    if not backends:
        print("WARN: no real backends available; falling back to mock for reproducible artifact generation")
        from adapters.mock_adapter import MockBackend

        backends = [MockBackend(model="mock", replies={"default": "fallback response"})]
        available = ["mock"]
    return backends, available


def _run_dir(mission_id: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    path = ROOT / "runs" / mission_id / stamp
    path.mkdir(parents=True, exist_ok=True)
    return path


def _serialize_response(resp) -> dict:
    return {
        "model": resp.model,
        "text": resp.text,
        "metadata": resp.metadata or {},
    }


def cmd_run(args: argparse.Namespace) -> int:
    mission = _load_mission(args.mission)
    backends, available = _build_backends(mission.get("providers", ["mock"]))
    if args.providers:
        backends, available = _build_backends(args.providers)
    from core.dispatcher import Dispatcher
    from core.runner import MissionRunner, Mission

    dispatcher = Dispatcher(backends=backends)
    runner = MissionRunner(dispatcher=dispatcher)
    mission_obj = Mission(
        id=str(mission["id"]),
        objective=str(mission.get("objective", "")),
        questions=list(mission.get("questions", [])),
        measurements=["agreement", "contradictions", "EPS", "MIS", "VG"],
    )
    results = runner.run_mission(mission_obj)
    run_dir = _run_dir(str(mission["id"]))
    prompts = {
        "mission_id": mission["id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "providers": available,
        "questions": mission.get("questions", []),
    }
    (run_dir / "prompts.json").write_text(json.dumps(prompts, indent=2), encoding="utf-8")
    responses_dir = run_dir / "responses"
    responses_dir.mkdir(exist_ok=True)
    response_rows = []
    for result in results:
        row = {
            "question": result.question,
            "raw_responses": [_serialize_response(r) for r in result.raw_responses],
            "report": result.report.to_dict(),
        }
        response_rows.append(row)
    report = {
        "mission": str(mission["id"]),
        "models": len(available),
        "claims": sum(len(r.report.claims) for r in results),
        "agreement": results[0].report.confidence.agreement if results else 0.0,
        "contradictions": sum(len(r.report.contradictions) for r in results),
        "evidence_required": sum(r.report.confidence.details.get("evidence_required", 0) for r in results),
        "verification_confidence": sum(r.report.confidence.score for r in results) / max(len(results), 1),
    }
    (run_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    provenance = {
        "providers": available,
        "run_id": run_dir.name,
        "mission_id": mission["id"],
        "per_question": [
            {
                "question": r.question,
                "models": [x.model for x in r.raw_responses],
                "versions": [x.metadata.get("version", "unknown") for x in r.raw_responses],
                "timestamps": [x.metadata.get("timestamp") for x in r.raw_responses],
            }
            for r in results
        ],
    }
    (run_dir / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"ARTIFACT_DIR={run_dir}")
    return 0


def cmd_verify(_args: argparse.Namespace) -> int:
    from mmvp import main as mmvp_main

    return mmvp_main()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mmvp")
    sub = parser.add_subparsers(dest="command")
    run = sub.add_parser("run", help="Run a live mission")
    run.add_argument("--mission", required=True, help="Mission ID, e.g. 003_live_backend_validation")
    run.add_argument("--providers", nargs="*", default=None, help="Override providers, e.g. mock")
    verify = sub.add_parser("verify", help="Run L0/L1 verification gate")
    verify.set_defaults(func=cmd_verify)
    run.set_defaults(func=cmd_run)
    parser.set_defaults(func=cmd_verify)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        return args.func(args)
    return cmd_verify(args)


if __name__ == "__main__":
    raise SystemExit(main())

install:
	pip install -r requirements.txt

test:
	pytest tests -v

verify:
	python -m mmvp
	@echo "L1 verification complete."

run: verify
	PYTHONPATH=. python -c "from core.runner import MissionRunner; print('runner ok')"

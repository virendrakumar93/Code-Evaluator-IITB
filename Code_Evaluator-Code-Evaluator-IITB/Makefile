.PHONY: setup run run-no-llm consistency clean help

setup:
	pip install -r requirements.txt

run: setup
	python cli.py --evaluate all --consistency-check

run-no-llm: setup
	python cli.py --evaluate all --consistency-check --no-llm

consistency: setup
	python cli.py --consistency-check --consistency-samples 10

evaluate-single:
	python cli.py --evaluate $(PROBLEM) --submission $(SUBMISSION)

clean:
	rm -rf reports/*.md reports/*.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

help:
	@echo "Usage:"
	@echo "  make setup              - Install dependencies"
	@echo "  make run                - Run full evaluation pipeline"
	@echo "  make run-no-llm         - Run without LLM (deterministic only)"
	@echo "  make consistency        - Run consistency check only"
	@echo "  make evaluate-single PROBLEM=problem_1 SUBMISSION=correct_optimal"
	@echo "  make clean              - Remove generated reports"

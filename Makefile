.PHONY: install test run clean pipeline

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src

run:
	python -m src.pipeline

pipeline:
	python -m src.pipeline

clean:
	rm -rf data/raw/*.json data/processed/*.json data/reports/*.md
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache

init:
	pip install -r requirements.txt
	mkdir -p data/raw data/processed data/reports

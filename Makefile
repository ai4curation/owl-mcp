MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
.SUFFIXES:
.SECONDARY:

RUN = uv run
SRC = src
DOCDIR = docs

.PHONY: all clean test lint format install example help

help:
	@echo ""
	@echo "make all -- makes site locally"
	@echo "make install -- install dependencies"
	@echo "make test -- runs tests"
	@echo "make lint -- runs linters"
	@echo "make format -- formats the code"
	@echo "make testdoc -- builds docs and runs local test server"
	@echo "make deploy -- deploys site"
	@echo "make example -- runs the example script"
	@echo "make help -- show this help"
	@echo ""

setup: install

install:
	uv sync --all-extras

all: test lint format

test:
	$(RUN) pytest

lint:
	$(RUN) ruff check .

format:
	$(RUN) ruff format .

# Test documentation locally
serve: mkd-serve

deploy: mkd-deploy

# Deploy docs
deploy-doc:
	$(RUN) mkdocs gh-deploy

# docs directory
$(DOCDIR):
	mkdir -p $@

MKDOCS = $(RUN) mkdocs
mkd-%:
	$(MKDOCS) $*

testdoc: serve

example:
	$(RUN) python example.py

clean:
	rm -rf dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf site/
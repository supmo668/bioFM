# Reproducibility Makefile for the standalone paper.
# All recipes are deterministic and seed 2026.

SHELL := /bin/bash
PY ?= python3
TEX ?= pdflatex
BIB ?= bibtex
export PYTHONPATH := $(CURDIR)/src:$(PYTHONPATH)

CSV_DIR := experiments/out
FIG_DIR := figures
TAB_DIR := tables

.PHONY: all paper figures tables simulate clean distclean

all: paper

paper: figures tables
	$(TEX) -interaction=nonstopmode paper.tex
	$(BIB) paper
	$(TEX) -interaction=nonstopmode paper.tex
	$(TEX) -interaction=nonstopmode paper.tex
	@echo ""
	@echo "✓ paper.pdf built: $$(pdfinfo paper.pdf 2>/dev/null | grep Pages || echo 'multi-page PDF')"

simulate: $(CSV_DIR)/e1_metric_validation.csv

$(CSV_DIR)/e1_metric_validation.csv: experiments/simulate.py
	$(PY) experiments/simulate.py

figures: simulate
	$(PY) experiments/plot.py

tables: simulate
	$(PY) experiments/generate_tables.py

clean:
	rm -f paper.aux paper.bbl paper.blg paper.log paper.out paper.toc
	rm -f $(FIG_DIR)/*.pdf $(FIG_DIR)/*.png
	rm -f $(TAB_DIR)/*.tex
	rm -rf $(CSV_DIR)

distclean: clean
	rm -f paper.pdf

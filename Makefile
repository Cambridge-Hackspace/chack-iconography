# Portable across BSD make and GNU make: plain targets, no shell functions.

VERSION = 0.1.0

all: build

bootstrap:
	uv sync
	@command -v resvg >/dev/null 2>&1 || \
		test -x ${HOME}/.cargo/bin/resvg || \
		cargo install resvg --locked --version 0.48.1

build:
	ISOLEX_BIN="`bash ci/get-isolex.sh`" \
		PATH="${PATH}:${HOME}/.cargo/bin" uv run build.py

docs:
	ISOLEX_BIN="`bash ci/get-isolex.sh`"; \
		"$$ISOLEX_BIN" docs src > docs/lexicon-reference.md

test:
	ISOLEX_BIN="`bash ci/get-isolex.sh`" uv run pytest -q

dist: test build
	tar -cjf chack-iconography-${VERSION}.tbz2 -C dist \
		svg svg-light svg-states svg-states-light drawio drawio-light preview
	@echo "chack-iconography-${VERSION}.tbz2"

clean:
	rm -rf dist upload chack-iconography-*.tbz2

.PHONY: all bootstrap build docs test dist clean

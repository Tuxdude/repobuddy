TOP_DIR             := $(dir $(lastword $(MAKEFILE_LIST)))
PYTHON              := python
PYLINT              := pylint
PEP8                := pep8
PEP257              := pep257
COVERAGE            := coverage
COVERAGE_HTML_DIR   := coverage-html-report
BROWSER             := xdg-open
INSTALL_TEST_DEPS   := $(TOP_DIR)/repobuddy/tests/install-deps.sh
SRCS                := $(shell find . \( -path ./build \) -prune -o -name '*.py' -print)
SRCS_NO_TESTS       := $(shell find repobuddy -maxdepth 1 -name '*.py' -print)
PYTHON_VERSION      := $($(PYTHON) --version 2>&1 | sed 's/^Python \([0-9]\.[0-9]\)\.[0-9]$/\1/')
CLEANUP_FILES       := \
                       $$HOME/.local/bin/repobuddy \
                       $$HOME/.local/bin/test_repobuddy \
	               $$HOME/.local/lib/python$(PYTHON_VERSION)/site-packages/RepoBuddy*.egg* \
                       *.egg-info \
                       build \
                       dist \
		       $(COVERAGE_HTML_DIR)
MAKEFLAGS 	    += --no-print-directory

dev-install:
	@$(PYTHON) setup.py develop --user --prefix=

dev-uninstall:
	@$(PYTHON) setup.py develop --uninstall
	$(MAKE) clean

sdist:
	@$(PYTHON) setup.py sdist

install:
	@$(PYTHON) setup.py install

install-test-deps:
	@$(INSTALL_TEST_DEPS)

clean:
	@rm -rf $(CLEANUP_FILES)
	@find . -name '*.py,cover' -print0 | xargs -0 -r rm -f

docs:
	@$(MAKE) -C ./docs clean && $(MAKE) -C ./docs html

pep8:
	@echo "Running $@ ..."
	@$(PEP8) $(SRCS)
	@echo

pep257:
	@echo "Running $@ ..."
	@$(PEP257) --explain $(SRCS_NO_TESTS)
	@echo

pylint:
	@$(PYLINT) --rcfile=.pylintrc --reports=n --include-ids=y $(SRCS)

pylint-report:
	@$(PYLINT) --rcfile=.pylintrc --reports=y --include-ids=y $(SRCS)

coverage-annotate: coverage
	@$(COVERAGE) html -d $(COVERAGE_HTML_DIR)
	@$(BROWSER) $(COVERAGE_HTML_DIR)/index.html

coverage:
	@$(COVERAGE) erase
	@($(COVERAGE) run ./run_tests.py && \
	    $(COVERAGE) report && echo) || ($(COVERAGE) report && echo && /bin/false)

ifeq ($(REPOBUDDY_TESTS),)
test:
	@$(MAKE) coverage || ($(MAKE) pep8 pep257 && /bin/false)
	@$(MAKE) pep8 pep257

else
coverage:REPOBUDDY_TESTS=

test:
	@./run_tests.py && $(MAKE) pep8 pep257 || ($(MAKE) pep8 pep257 && /bin/false)
endif

.PHONY: dev-install dev-uninstall sdist install install-test-deps clean docs
.PHONY: pep8 pep257 pylint pylint-report test coverage converage-annotate

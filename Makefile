PYTHON              := python
PYLINT              := pylint
PEP8                := pep8
COVERAGE            := coverage
COVERAGE_HTML_DIR   := coverage-html-report
BROWSER             := chromium
SRCS                := $(shell find . \( -path ./build -o -path ./docs \) -prune -o -name '*.py' -print)
CLEANUP_FILES       := \
                       $$HOME/.local/bin/repobuddy \
	               $$HOME/.local/lib/python2.7/site-packages/RepoBuddy*.egg \
                       *.egg-info \
                       build \
                       dist \
		       $(COVERAGE_HTML_DIR)
MAKEFLAGS 	    += --no-print-directory

dev-install:
	@$(PYTHON) setup.py develop

dev-uninstall:
	@$(PYTHON) setup.py develop --uninstall
	$(MAKE) clean

sdist:
	@$(PYTHON) setup.py sdist

install:
	@$(PYTHON) setup.py install

clean:
	@rm -rf $(CLEANUP_FILES)
	@find . -name '*.py,cover' -print0 | xargs -0 -r rm

pep8:
	@$(PEP8) $(SRCS)

pylint:
	@$(PYLINT) --rcfile=.pylintrc -r n -i y -d C0111 $(SRCS)

pylint-report:
	@$(PYLINT) --rcfile=.pylintrc -r y -i y -d C0111 $(SRCS)

coverage-annotate: coverage
	@$(COVERAGE) html -d $(COVERAGE_HTML_DIR)
	@$(BROWSER) $(COVERAGE_HTML_DIR)/index.html

coverage:
	@$(COVERAGE) erase
	@($(COVERAGE) run ./run_tests.py && \
	    $(COVERAGE) report && echo) || ($(COVERAGE) report && echo && /bin/false)

ifeq ($(REPOBUDDY_TESTS),)
test:
	@$(MAKE) coverage || ($(MAKE) pep8 && /bin/false)
	@$(MAKE) pep8

else
coverage:REPOBUDDY_TESTS=

test:
	@./run_tests.py && $(MAKE) pep8 || ($(MAKE) pep8 && /bin/false)
endif

.PHONY: dev-install dev-uninstall sdist install install-user clean
.PHONY: pep8 pylint pylint-report test coverage converage-annotate

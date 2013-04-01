PYTHON              := python
PYLINT              := pylint
PEP8                := pep8
COVERAGE            := coverage
COVERAGE_HTML_DIR   := coverage-html
BROWSER             := chromium
SRCS                := $(shell find . -path ./build -prune -o -name '*.py' -print)
CLEANUP_FILES       := \
                       $$HOME/.local/bin/repobuddy \
	               $$HOME/.local/lib/python2.7/site-packages/RepoBuddy*.egg \
                       *.egg-info \
                       build \
                       dist \
		       $(COVERAGE_HTML_DIR)

dev-install:
	@$(PYTHON) setup.py develop

dev-uninstall:
	@$(PYTHON) setup.py develop --uninstall
	$(MAKE) clean

sdist:
	@$(PYTHON) setup.py sdist

install:
	@$(PYTHON) setup.py install

install-user:
	@$(PYTHON) setup.py install --user

clean:
	@rm -rf $(CLEANUP_FILES)
	@find . -name '*.py,cover' -print0 | xargs -0 -r rm

pep8:
	@$(PEP8) $(SRCS)

pylint:
	@$(PYLINT) --rcfile=.pylintrc -r n -i y -d C0111 $(SRCS)

pylint-report:
	@$(PYLINT) --rcfile=.pylintrc -r y -i y -d C0111 $(SRCS)

test:
	@$(PYTHON) ./run_tests.py

coverage:
	@$(COVERAGE) erase
	@($(COVERAGE) run --source=repobuddy ./run_tests.py && \
	    $(COVERAGE) report) || ($(COVERAGE) report && /bin/false)

coverage-annotate: coverage
	@$(COVERAGE) html -d $(COVERAGE_HTML_DIR)
	@$(BROWSER) $(COVERAGE_HTML_DIR)/index.html

.PHONY: dev-install dev-uninstall sdist install install-user clean
.PHONY: pep8 pylint pylint-report test coverage converage-annotate

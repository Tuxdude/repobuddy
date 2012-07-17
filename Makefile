PYTHON   := python
PYLINT   := pylint
PEP8     := pep8
COVERAGE := coverage
SRCS     := $(shell find . -path ./build -prune -o -name '*.py' -print)
CLEANUP_FILES := \
            $$HOME/.local/bin/repobuddy \
            $$HOME/.local/lib/python2.7/site-packages/RepoBuddy*.egg \
            *.egg-info \
            build \
            dist

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
	@rm -rf *.egg-info build dist
	@find . -name '*,cover' | xargs rm

pep8:
	@$(PEP8) $(SRCS)

pylint:
	@$(PYLINT) --rcfile=.pylintrc -r n -i y -d C0111 $(SRCS)

pylint-report:
	@$(PYLINT) --rcfile=.pylintrc -r y -i y -d C0111 $(SRCS)

coverage:
	@$(COVERAGE) erase
	@$(COVERAGE) run ./run_tests.py
	@$(COVERAGE) report

coverage-annotate: coverage
	@$(COVERAGE) annotate

.PHONY: develop sdist clean pep8 pylint pylint-report

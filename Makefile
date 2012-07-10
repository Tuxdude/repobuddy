PYTHON := python
PYLINT := pylint
PEP8   := pep8
SRCS   := $(shell find . -path ./build -prune -o -name '*.py' -print)

develop:
	@$(PYTHON) setup.py develop

sdist:
	$(PYTHON) setup.py sdist

clean:
	$(PYTHON) setup.py develop --uninstall
	@rm -rf *.egg-info dist

pep8:
	@$(PEP8) $(SRCS)

pylint:
	@$(PYLINT) -r n -d C0111 $(SRCS)

pylint-report:
	@$(PYLINT) -r y -d C0111 $(SRCS)

.PHONY: develop sdist clean pep8 pylint pylint-report


.PHONY: db test pep8 clean check-venv check-venv

# clean out potentially stale pyc files
clean:
	@find . -name "*.pyc" -exec rm {} \;

# check that virtualenv is enabled
check-venv:
ifndef VIRTUAL_ENV
	$(error VIRTUAL_ENV is undefined, try "workon" command)
endif

# Install pip requirements.txt file
reqs: check-venv
	pip install --upgrade -r requirements.txt

# Show all occurence of same error
# Exclude the static directory, since it's auto-generated
PEP8_OPTS=--repeat --exclude=static,south_migrations,migrations,js,doc --show-source

pep8: check-venv
	python setup.py pep8 $(PEP8_OPTS)

FLAKE8_OPTS = --max-complexity 10 --exclude='migrations,south_migrations'
flake8: check-venv
	flake8 $(FLAKE8_OPTS) . | tee flake8.log

test: check-venv clean
	python -Wall manage.py test -v 2

travis-tests: check-venv
	@echo "travis_fold:start:flake8"
	make flake8
	@echo "travis_fold:end:flake8"

	coverage erase
	@echo "travis_fold:start:test"
	coverage run $(COVERAGE_ARGS) ./manage.py test --keepdb -v 2
	@echo "travis_fold:end:test"

	@echo "travis_fold:start:coverage"
	coverage report
	coverage html
	@echo "travis_fold:end:coverage"


#
# code coverage
#

COVERAGE_ARGS=--source=x509_auth --omit=x509_auth/south_migrations/*

coverage: check-venv
	coverage erase
	-coverage run $(COVERAGE_ARGS) ./manage.py test -v 2
	coverage report
	coverage html
	@echo "See ./htmlcov/index.html for coverage report"

#
# convenience
#

develop-%: check-venv
	cd ../$*; python setup.py develop -N


.PHONY: test

test:
	nosetests bevel/tests/ --with-coverage --cover-package bevel

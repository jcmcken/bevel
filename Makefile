.PHONY: test

test:
	env -i nosetests bevel/tests/ --with-coverage --cover-package bevel -v -s

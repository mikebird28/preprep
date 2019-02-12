

local:
	pip install -e ./

upload:
	python setup.py sdist
	twine upload dist/*

clean:
	rm -f *.pyc
	rm -f preprep/*.pyc
	rm -f test/*.pyc
	rm -rf dist

test:
	python -m unittest test.test_param_holder
	python -m unittest test.test_savefile
	python -m unittest test.test_operator
	python -m unittest test.test_calc_graph
	python -m unittest test.test_preprep

.PHONY: local clean test upload



local:
	pip install -e ./

clean:
	rm -f *.pyc
	rm -f preprep/*.pyc
	rm -f test/*.pyc

test:
	python -m unittest test.test_preprep
	python -m unittest test.test_operator
	python -m unittest test.test_calc_graph
	python -m unittest test.test_savefile

.PHONY: local clean test

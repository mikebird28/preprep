

local:
	pip install -e ./

clean:
	rm -f *.pyc
	rm -f preprep/*.pyc

test:
	python -m unittest test.test_operator.py
	python -m unittest test.test_calc_graph.py

.PHONY local clean default

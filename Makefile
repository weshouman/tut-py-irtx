
test:
	python -m xmlrunner discover -o out

test_verbose:
	python -m xmlrunner discover -v -o out

test_in_progress:
	python -m xmlrunner tests/test_tfidf.py -o out

clean_reports:
	rm out/*.xml


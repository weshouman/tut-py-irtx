
test:
	python -m xmlrunner discover -o out

clean_reports:
	rm out/*.xml

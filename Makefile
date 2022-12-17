
test:
	python -m xmlrunner discover -o out

test_verbose:
	python -m xmlrunner discover -v -o out

test_in_progress:
	python -m xmlrunner tests/test_util.py -o out

test_method_in_progress:
	python -m xmlrunner tests.test_inv_index.InvIndexTest.test01_inverted_index_generation -o out
	#python -m xmlrunner tests.test_ranking.RankingTest.test01_calc_rank -o out

clean_reports:
	rm out/*.xml


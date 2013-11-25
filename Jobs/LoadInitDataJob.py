#!/usr/bin/env python3.3

import sys


class LoadInitDataJob:
	def map(self):
		return

	def reduce(self):
		for equation in sys.stdin:
			equationIndex, equation = equation.strip().split('\t')
			print('{0}\t{1}'.format(equationIndex, equation))


if __name__ == "__main__":
	Job = LoadInitDataJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
#!/usr/bin/env python3.3

import sys


class MergeSimplificationEquationsJob:
	def map(self):
		return

	def reduce(self):
		equationIndex = 0
		for result in sys.stdin:
			splits = result.strip().split('\t')
			#we got equation
			if len(splits) == 3:
				equation = splits[2]
				print('{0}\t{1}'.format(equationIndex, equation))
				equationIndex += 1


if __name__ == "__main__":
	Job = MergeSimplificationEquationsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
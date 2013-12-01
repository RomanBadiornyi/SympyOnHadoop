#!/usr/bin/env python3.3

import sys


class MergeSimplificationUndeterminedResultsJob:
	def map(self):
		return

	def reduce(self):
		for result in sys.stdin:
			splits = result.strip().split('\t')
			#we got undetermined result
			if len(splits) == 4:
				block = splits[0]
				index = splits[1]
				symbol = splits[2]
				result = splits[3]
				print('{0}\t{1}\t{2}\t{3}'.format(block, index, symbol, result))


if __name__ == "__main__":
	Job = MergeSimplificationUndeterminedResultsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
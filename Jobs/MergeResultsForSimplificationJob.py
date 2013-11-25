#!/usr/bin/env python3.3

import sys


class MergeResultsForSimplificationJob:
	def map(self):
		return

	def reduce(self, blocksCount):
		for resultLine in sys.stdin:
			resultBlock, index, symbol, result = resultLine.strip().split('\t')
			for block in range(int(blocksCount)):
				print('{0}\t{1}\t{2}\t{3}'.format(block, index, symbol, result))


if __name__ == "__main__":
	Job = MergeResultsForSimplificationJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce(sys.argv[2])
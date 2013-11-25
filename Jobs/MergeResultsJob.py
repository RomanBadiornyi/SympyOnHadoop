#!/usr/bin/env python3.3

import sys

from Jobs.Utils import *


class MergeResultsJob:
	def map(self):
		return

	def reduce(self):
		for result in sys.stdin:
			block, resultKey, resultValue = result.strip().split('\t')
			index = str(getSymbolIndex(resultKey))
			print('{0}\t{1}\t{2}\t{3}'.format(block, index, resultKey, resultValue))

if __name__ == "__main__":
	Job = MergeResultsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
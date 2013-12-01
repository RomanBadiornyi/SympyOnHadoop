#!/usr/bin/env python3.3

import sys
from Jobs.Utils import *


class CollectFinalResultsJob:
	def map(self):
		return

	def reduce(self):
		for result in sys.stdin:
			block, index, resultKey, resultValue = result.strip().split('\t')
			if checkIfResultReady(resultValue):
				print('{0}\t{1}\t{2}\t{3}'.format("-1", index, resultKey, resultValue))


if __name__ == "__main__":
	Job = CollectFinalResultsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
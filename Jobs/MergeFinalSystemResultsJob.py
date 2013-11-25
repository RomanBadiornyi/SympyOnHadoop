#!/usr/bin/env python3.3

import sys


class MergeFinalSystemResultsJob:
	def map(self):
		return

	def reduce(self):
		previousSymbolIndex = -1
		for result in sys.stdin:
			splits = result.strip().split('\t')
			if len(splits) == 4:
				index = splits[1]
				symbol = splits[2]
				result = splits[3]
				if index != previousSymbolIndex:
					print('{0}\t{1}'.format(symbol, result))
					previousSymbolIndex = index

if __name__ == "__main__":
	Job = MergeFinalSystemResultsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
#!/usr/bin/env python3.3

import sys


class MergeFinalSystemResultsJob:
	def map(self):
		return

	def reduce(self, debug, inputFilename, secondInputFileName, outputFilename):
		output = None
		if debug:
			input = open(inputFilename, 'r')
			output = open(outputFilename, 'a')
		else:
			input = sys.stdin
		previousSymbolIndex = -1
		for result in input:
			splits = result.strip().split('\t')
			if len(splits) == 4:
				index = splits[1]
				symbol = splits[2]
				result = splits[3]
				if index != previousSymbolIndex:
					if output is not None:
						output.write('{0}\t{1}'.format(symbol, result))
					print('{0}\t{1}'.format(symbol, result))
					previousSymbolIndex = index

if __name__ == "__main__":
	Job = MergeFinalSystemResultsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce(sys.argv[2:])
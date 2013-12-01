#!/usr/bin/env python3.3

import sys
from glob import glob
from debian.debtags import output
from Jobs.Utils import getSymbolIndex
from Jobs.Utils import decodeExpression


class PrepareResults:

	def map(self, blocksCount, debug=False, inputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]

		for input in inputList:
			for resultLine in input:
				resultBlock, index, symbol, result = resultLine.strip().split('\t')
				for block in range(int(blocksCount)):
					if output is not None:
						output.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(3, block, index, symbol, result))
					else:
						print('{0}\t{1}\t{2}\t{3}\t{4}'.format(3, block, index, symbol, result))
			if debug:
				input.close()
		if output is not None:
			output.close()

	def reduce(self):
		return

if __name__ == "__main__":
	Job = PrepareResults()
	if sys.argv[1] == "map":
		if len(sys.argv[2:]) > 1:
			Job.map(blocksCount=sys.argv[2], debug=sys.argv[3], inputFilename=sys.argv[4], outputFilename=sys.argv[5])
		else:
			Job.map(blocksCount=sys.argv[2])
	elif sys.argv[1] == "reduce":
		Job.reduce()
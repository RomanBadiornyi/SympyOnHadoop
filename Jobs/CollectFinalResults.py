#!/usr/bin/env python3.3

import sys
from glob import glob


class CollectFinalResults:
	def map(self, debug=False, inputFilename=None, secondInputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			inputList.append(open(secondInputFilename, "r"))
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]
		for input in inputList:
			for result in input:
				splits = result.strip().split('\t')
				#we got final result
				if len(splits) == 3:
					symbol = splits[1]
					result = splits[2]
					if output is not None:
						output.write('{0}\t{1}\t{2}\n'.format("-1", symbol, result))
					else:
						print('{0}\t{1}\t{2}'.format("-1", symbol, result))
			if debug:
				input.close()
		if output is not None:
			output.close()

	def reduce(self):
		return


if __name__ == "__main__":
	Job = CollectFinalResults()
	if sys.argv[1] == "map":
		if len(sys.argv[2:]) > 1:
			Job.map(debug=sys.argv[2], inputFilename=sys.argv[3], secondInputFilename = sys.argv[4], outputFilename=sys.argv[5])
		else:
			Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
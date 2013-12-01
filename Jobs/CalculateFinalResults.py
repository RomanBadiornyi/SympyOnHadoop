#!/usr/bin/env python3.3

import sys
from glob import glob


class CalculateFinalResults:

	def map(self):
		return

	def reduce(self, debug=False, inputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]
		finalResults = {}
		count = 0
		for input in inputList:
			for resultLine in input:
				splits = resultLine.strip().split('\t')
				if len(splits) == 3:
					index = splits[0]
					value = splits[2]
					if index not in finalResults:
						finalResults[index] = value
						count += 1
			if debug:
				input.close()

		if output is not None:
			output.write(str(count))
		else:
			print("{0}".format(str(count)))
		if output is not None:
			output.close()

if __name__ == "__main__":
	Job = CalculateFinalResults()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 0:
			Job.reduce(debug=sys.argv[3], inputFilename=sys.argv[4], outputFilename=sys.argv[5])
		else:
			Job.reduce()
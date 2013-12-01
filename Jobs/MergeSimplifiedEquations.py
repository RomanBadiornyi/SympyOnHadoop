#!/usr/bin/env python3.3

import sys
from glob import glob


class MergeSimplifiedEquations:

	def map(self, debug=False, inputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]
		for input in inputList:
			for resultLine in input:
				splits = resultLine.strip().split('\t')
				#we got equation
				if len(splits) == 3:
					index = splits[1]
					equation = splits[2]
					if output is not None:
						output.write('{0}\t{1}\n'.format(index, equation))
					else:
						print('{0}\t{1}'.format(index, equation))
			if debug:
				input.close()
		if output is not None:
			output.close()

	def reduce(self):
		return

if __name__ == "__main__":
	Job = MergeSimplifiedEquations()
	if sys.argv[1] == "map":
		if len(sys.argv[2:]) > 1:
			Job.map(debug=sys.argv[2], inputFilename=sys.argv[3], outputFilename=sys.argv[4])
		else:
			Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
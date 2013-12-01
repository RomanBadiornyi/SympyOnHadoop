#!/usr/bin/env python3.3

import sys
from sympy import expand
from Jobs.Utils import encodeExpression
from Jobs.Utils import decodeExpression


class SerializeEquations:

	def map(self):
		return

	def reduce(self, debug=False, inputFilename=None, secondInputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(inputFilename, 'r'), open(secondInputFilename, 'r')]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]

		symbols = set()
		for input in inputList:
			for equation in input:
				splits = equation.strip().split('\t')
				if splits[0] == '-1':
					symbols = decodeExpression(splits[1])
				else:
					equationIndex = splits[0]
					equation = expand(splits[1])
					if output is not None:
						output.write("{0}\t{1}\n".format(equationIndex, encodeExpression((equation, symbols))))
					else:
						print("{0}\t{1}".format(equationIndex, encodeExpression((equation, symbols))))
		if debug:
			input.close()
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = SerializeEquations()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 0:
			Job.reduce(debug=sys.argv[2], inputFilename=sys.argv[3], secondInputFilename=sys.argv[4], outputFilename=sys.argv[5])
		else:
			Job.reduce()
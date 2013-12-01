#!/usr/bin/env python3.3

import sys
from sympy.core import numbers
from Jobs.Utils import *


class ReplaceVariablesWithResults:
	def map(self):
		return

	def reduce(self, debug=False, inputFilename=None, secondInputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(inputFilename, "r"), open(secondInputFilename, "r")]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]
		results = {}
		for input in inputList:
			for line in input:
				splits = line.strip().split('\t')
				if len(splits) != 2:
					resultKey = decodeExpression(splits[1])
					resultValue = decodeExpression(splits[2])
					results[resultKey] = resultValue
				else:
					equationIndex = splits[0]
					equation, symbols = decodeExpression(splits[1])
					for resultKey in results.keys():
						if equation.has(resultKey):
							equation = equation.subs(resultKey, results[resultKey])
					if not isinstance(equation, numbers.Zero):
						if output is not None:
							output.write('{0}\t{1}\n'.format(equationIndex, encodeExpression((equation, symbols))))
						else:
							print('{0}\t{1}'.format(equationIndex, encodeExpression((equation, symbols))))


if __name__ == "__main__":
	Job = ReplaceVariablesWithResults()
	if sys.argv[1] == "map":
		Job.reduce()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 1:
			Job.reduce(debug=sys.argv[2], inputFilename=sys.argv[3], secondInputFilename = sys.argv[4], outputFilename=sys.argv[5])
		else:
			Job.reduce()
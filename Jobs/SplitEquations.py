#!/usr/bin/env python3.3

import sys
from sympy import Poly
from Jobs.Utils import decodeExpression


class SplitEquations:
	def map(self):
		return

	def reduce(self, debug=False, inputFilename=None, outputFilename=None):
		previousLeftBlockRegion = -1
		previousRightBlockRegion = -1
		equationCount = 0
		partIndex = 0
		equationInPartIndex = 0

		output = None
		if debug:
			input = open(inputFilename, 'r')
			output = open(outputFilename, 'w')
		else:
			input = sys.stdin

		for strEquation in input:
			equationCount += 1
			index, strEquation = strEquation.strip().split('\t')
			equation, symbols = decodeExpression(strEquation)
			equation = Poly(equation, symbols)
			equationCoefficients = [0] * len(symbols)
			for monom, coeff in equation.terms():
				try:
					i = list(monom).index(1)
					equationCoefficients[i] = 1 if coeff != 0 else 0
				except ValueError:
					continue

			equationLen = len(equationCoefficients)
			rightColumnIndex = equationLen - 1
			leftColumnIndex = 0

			while leftColumnIndex < equationLen and equationCoefficients[leftColumnIndex] != 1:
				leftColumnIndex += 1
			while rightColumnIndex > 0 and equationCoefficients[rightColumnIndex] != 1:
				rightColumnIndex -= 1

			if previousLeftBlockRegion != leftColumnIndex or previousRightBlockRegion != rightColumnIndex:
				if equationInPartIndex > 0:
					partIndex += 1
					equationInPartIndex = 0
				previousLeftBlockRegion = leftColumnIndex
				previousRightBlockRegion = rightColumnIndex
			if output is not None:
				output.write('{0}\t{1}\t{2}\n'.format(str(partIndex), index, strEquation))
			else:
				print('{0}\t{1}\t{2}'.format(str(partIndex), index, strEquation))
			equationInPartIndex += 1
		if debug:
			input.close()
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = SplitEquations()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 0:
			Job.reduce(debug=sys.argv[2], inputFilename=sys.argv[3], outputFilename=sys.argv[4])
		else:
			Job.reduce()
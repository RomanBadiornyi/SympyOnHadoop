#!/usr/bin/env python3.3

import sys

from sympy import expand
from sympy.core import numbers

from Jobs.Utils import *


class ReplaceVariablesWithResultsJob:
	def map(self):
		return

	def reduce(self):
		results = {}
		for line in sys.stdin:
			splits = line.strip().split('\t')
			if len(splits) != 2:
				resultKey = splits[2]
				resultValue = splits[3]
				results[resultKey] = resultValue
			else:
				equationIndex = splits[0]
				equation = splits[1]
				for resultKey in results.keys():
					equation = replaceSymbol(equation, resultKey, results[resultKey])
				simplifiedEquation = expand(equation, power_exp=False, log=False)
				if not isinstance(simplifiedEquation, numbers.Zero):
					print('{0}\t{1}'.format(equationIndex, simplifiedEquation))


if __name__ == "__main__":
	Job = ReplaceVariablesWithResultsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
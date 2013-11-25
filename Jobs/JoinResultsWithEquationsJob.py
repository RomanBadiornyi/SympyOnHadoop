#!/usr/bin/env python3.3

import sys


class JoinResultsWithEquationsJob:
	def map(self):
		for line in sys.stdin:
			line = line.strip()
			splits = line.split('\t')
			indexEq = "-1"
			equation = "-1"
			indexR = "-1"
			symbolR = "-1"
			result = "-1"
			#we got equation
			if len(splits) == 3:
				block, indexEq, equation = splits
			#we got result
			else:
				block, indexR, symbolR, result = splits
			print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(block, indexEq, equation, indexR, symbolR, result))

	def reduce(self):
		currentIndexEq = "-1"
		currentEq = ""

		currentIndexR = "-1"
		currentSymbolR = ""
		currentResult = ""
		for line in sys.stdin:
			line = line.strip()
			block, indexEq, equation, indexR, symbolR, result = line.split('\t')
			if indexEq != "-1":
				currentIndexEq = indexEq
				currentEq = equation
			elif indexR != "-1":
				currentIndexR = indexR
				currentSymbolR = symbolR
				currentResult = result

			if currentIndexEq != "-1" and currentIndexR != "-1":
				print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(block, currentIndexEq, currentEq, currentIndexR, currentSymbolR,
															currentResult))


if __name__ == "__main__":
	Job = JoinResultsWithEquationsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
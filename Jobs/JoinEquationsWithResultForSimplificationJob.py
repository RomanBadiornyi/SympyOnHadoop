#!/usr/bin/env python3.3

import sys


class JoinEquationsWithResultForSimplificationJob:
	def map(self):
		for line in sys.stdin:
			line = line.strip()
			splits = line.split('\t')
			block = "-1"
			indexEq = "-1"
			equation = "-1"
			indexR = "-1"
			symbolR = "-1"
			result = "-1"
			_indexR = "-1"
			_symbolR = "-1"
			_result = "-1"
			#we got equations with block results
			if len(splits) == 6:
				block = splits[0]
				indexEq = splits[1]
				equation = splits[2]
				indexR = splits[3]
				symbolR = splits[4]
				result = splits[5]
			#we got item from all results
			elif len(splits) == 4:
				block = splits[0]
				_indexR = splits[1]
				_symbolR = splits[2]
				_result = splits[3]
			print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}'.format(block, indexEq, equation, indexR, symbolR, result,
																	   _indexR, _symbolR, _result))

	def reduce(self):
		currentIndexEq = "-1"
		currentEq = ""
		currentIndexR = ""
		currentSymbolR = ""
		currentResult = ""

		_currentIndexR = "-1"
		_currentSymbolR = ""
		_currentResult = ""
		for line in sys.stdin:
			line = line.strip()
			block, indexEq, equation, indexR, symbolR, result, _indexR, _symbolR, _result = line.split('\t')
			if indexEq != "-1":
				currentIndexEq = indexEq
				currentEq = equation
				currentIndexR = indexR
				currentSymbolR = symbolR
				currentResult = result
			elif _indexR != "-1":
				_currentIndexR = _indexR
				_currentSymbolR = _symbolR
				_currentResult = _result

			if currentIndexEq != "-1" and _currentIndexR != "-1":
				print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}'.format(block, _currentIndexR, currentIndexEq, currentEq,
																		   currentIndexR, currentSymbolR, currentResult,
																		   _currentSymbolR, _currentResult))

if __name__ == "__main__":
	Job = JoinEquationsWithResultForSimplificationJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()
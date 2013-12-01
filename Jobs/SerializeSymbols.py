#!/usr/bin/env python3.3

import sys
import pickle
import base64
from Jobs.Utils import *


class SerializeSymbolsJob:

	def map(self):
		return

	def reduce(self, debug, inputFilename, outputFilename):
		output = None
		if debug:
			input = open(inputFilename, 'r')
			output = open(outputFilename, 'w')
		else:
			input = sys.stdin

		symbols = []
		strSymbols = set()
		for equation in input:
			equationIndex, equation = equation.strip().split('\t')
			symbolsList = getSymbolsList(equation)
			[strSymbols.add(symbol) for symbol in symbolsList]
		#sort symbols by indexes
		symbolPairs = [(getSymbolIndex(symbol), symbol) for symbol in strSymbols]
		symbolsByIndexes = dict((symbol, index) for symbol, index in symbolPairs)
		indexesList = [index for index in symbolsByIndexes.keys()]
		indexesList.sort()
		if output is not None:
			output.write("-1\t{0}\n".format(base64.b64encode(pickle.dumps(symbols)).decode("latin1")))
		else:
			print("-1\t{0}".format(base64.b64encode(pickle.dumps(symbols)).decode("latin1")))

		if debug:
			input.close()
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = SerializeSymbolsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce(sys.argv[2:])
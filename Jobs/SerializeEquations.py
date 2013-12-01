#!/usr/bin/env python3.3

import sys
import pickle
import base64
from sympy import Poly


class SerializeEquations:

	def map(self):
		return

	def reduce(self, debug, inputFilename, secondInputFilename, outputFilename):
		output = None
		if debug:
			input = open(inputFilename, 'r')
			output = open(outputFilename, 'w')
		else:
			input = sys.stdin

		symbols = set()
		for equation in input:
			splits = equation.strip().split('\t')
			if splits[0] == '-1':
				symbols = pickle.loads(base64.b64decode(splits[1].encode("latin1")))
			else:
				equationIndex = splits[0]
				equation = Poly(splits[1], symbols)
				if output is not None:
					output.write("{0}\t{1}\n".format(equationIndex, base64.b64encode(pickle.dumps(equation)).decode("latin1")))
				else:
					print("{0}\t{1}".format(equationIndex, base64.b64encode(pickle.dumps(equation)).decode("latin1")))
		if debug:
			input = open(secondInputFilename, 'r')
			for equation in input:
				splits = equation.strip().split('\t')
				if splits[0] == '-1':
					symbols = pickle.loads(base64.b64decode(splits[1].encode("latin1")))
				else:
					equationIndex = splits[0]
					equation = Poly(splits[1], symbols)
					if output is not None:
						output.write("{0}\t{1}\n".format(equationIndex, base64.b64encode(pickle.dumps(equation)).decode("latin1")))
					else:
						print("{0}\t{1}".format(equationIndex, base64.b64encode(pickle.dumps(equation)).decode("latin1")))

		if debug:
			input.close()
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = SerializeEquations()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce(sys.argv[2:])
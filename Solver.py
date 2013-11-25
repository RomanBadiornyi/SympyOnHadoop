#!/usr/bin/env python3.3

import os
import sys
import subprocess
from datetime import datetime
from datetime import timedelta

from Commands import *
from Jobs.Utils import *


def HELP_FUNCTION_GET_BLOCKS_COUNT(input):
	input = open(input, 'r')
	partIndex = 0
	lineCount = 0
	for line in input:
		lineCount += 1
		partIndex, equationIndex, equation = line.strip().split('\t')
	if lineCount == 0:
		return 0
	else:
		return int(partIndex) + 1


def hadoopSimulation(args):
	start = datetime.now()

	os.system("rm -f FinalResults")

	resultsCount = 0
	equationsExists = True

	p = subprocess.Popen(MapInitDataCommand, shell=True)
	p.wait()

	SplittingToBlocksTotal = timedelta(0)
	ComputingResultsTotal = timedelta(0)
	MergingResultsTotal = timedelta(0)
	JoiningResultsTotal = timedelta(0)
	ResultSimplificationTotal = timedelta(0)
	MergingResultSimplificationTotal = timedelta(0)
	ReplacingWithResultsTotal = timedelta(0)

	print("Start computation: {0}\n".format(str(datetime.now())))

	os.system("touch UndeterminedResults")
	os.system("touch FinalResults")

	while equationsExists:
		operationStart = datetime.now()
		p = subprocess.Popen(SplitEquationsCommand, shell=True)
		p.wait()
		operationEnd = datetime.now()
		time = operationEnd - operationStart
		SplittingToBlocksTotal += time
		blocksCount = HELP_FUNCTION_GET_BLOCKS_COUNT('InputEquationsSplit')
		print("Splitting equations to blocks finished, execution time: {0}, blocks count: {1}\n".format(str(time), blocksCount))

		if blocksCount == 0:
			equationsExists = False

		operationStart = datetime.now()
		if not equationsExists:
			break

		processesList = []
		for reducerNumber in range(blocksCount):
			p = subprocess.Popen(ComputeEquationBlockCommand.format(reducerNumber), shell=True)
			processesList.append(p)
		[p.wait() for p in processesList]

		operationEnd = datetime.now()
		time = operationEnd - operationStart
		ComputingResultsTotal += time
		print("Computing results in blocks finished, execution time: {0}\n".format(str(time)))

		operationStart = datetime.now()
		p = subprocess.Popen(MergeResultsCommand, shell=True)
		p.wait()

		os.system("rm OutputResults*")
		finalResultsCount = getFinalResultsCount("MergedResults")
		resultsCount += finalResultsCount
		operationEnd = datetime.now()
		time = operationEnd - operationStart
		MergingResultsTotal += time
		print("Merging results finished, execution time: {0}\n".format(str(time)))

		if finalResultsCount == 0:
			operationStart = datetime.now()
			blocksCount = getBlocksCount("InputEquationsSplit")
			p = subprocess.Popen(MapResultsForSimplificationCommand.format(blocksCount), shell=True)
			p.wait()
			p = subprocess.Popen(JoinResultsWithEquationsCommand, shell=True)
			p.wait()
			p = subprocess.Popen(JoinEquationsWithResultForSimplificationCommand, shell=True)
			p.wait()

			os.system("rm ResultsForSimplification")
			os.system("rm EquationsWithResults")

			operationEnd = datetime.now()
			time = operationEnd - operationStart
			JoiningResultsTotal += time
			print("Joining results with equations finished, execution time: {0}\n".format(str(time)))

			operationStart = datetime.now()
			processesList = []
			for blockNumber in range(blocksCount):
				p = subprocess.Popen(SimplifyEquationsCommand.format(blockNumber), shell=True)
				processesList.append(p)
			[p.wait() for p in processesList]
			operationEnd = datetime.now()
			time = operationEnd - operationStart
			ResultSimplificationTotal += time
			print("Results simplification finished, execution time: {0}\n".format(str(time)))

			operationStart = datetime.now()
			os.system("rm EquationsWithResultsForSimplification")
			p = subprocess.Popen(MergeSimplificationResultsToInputEquationsCommand, shell=True)
			p.wait()
			os.system("cp UndeterminedResults UndeterminedResultsCopy")
			p = subprocess.Popen(MergeSimplificationResultsToUndeterminedResults, shell=True)
			p.wait()
			os.system("rm UndeterminedResultsCopy")
			operationEnd = datetime.now()
			time = operationEnd - operationStart
			MergingResultSimplificationTotal += time
			print("Merging of simplification results finished, execution time: {0}\n".format(str(time)))
			os.system("rm SimplificationResult*")
		else:
			operationStart = datetime.now()
			os.system("cp FinalResults FinalResultsCopy")
			p = subprocess.Popen(CollectFinalResultsCommand, shell=True)
			p.wait()
			os.system("rm FinalResultsCopy")
			p = subprocess.Popen(ReplaceVariablesWithFinalResultsCommand, shell=True)
			p.wait()
			operationEnd = datetime.now()
			time = operationEnd - operationStart
			ReplacingWithResultsTotal += time
			print("Results in equations replaced: {0}\n".format(str(time)))
		os.system("rm MergedResults")
	p = subprocess.Popen(MergeFinalSystemResultsCommand, shell=True)
	p.wait()
	os.system("rm InputEquations")
	os.system("rm InputEquationsSplit")
	os.system("rm FinalResults")
	os.system("rm UndeterminedResults")

	end = datetime.now()
	print('Execution time is: {0}'.format(str(end - start)))
	print('{0} ,Total execution time is: {1}'.format("Splitting to block operation", SplittingToBlocksTotal))
	print('{0} ,Total execution time is: {1}'.format("Computing results operation", ComputingResultsTotal))
	print('{0} ,Total execution time is: {1}'.format("Merging results operation", MergingResultsTotal))
	print('{0} ,Total execution time is: {1}'.format("Joining results operation", JoiningResultsTotal))
	print('{0} ,Total execution time is: {1}'.format("Results simplification operation", ResultSimplificationTotal))
	print('{0} ,Total execution time is: {1}'.format("Merging simplified results operation", MergingResultSimplificationTotal))
	print('{0} ,Total execution time is: {1}'.format("Replacing variables with results operation", ReplacingWithResultsTotal))


def getFinalResultsCount(resultsFile):
	resultsFile = open(resultsFile, 'r')
	count = 0
	for resultLine in resultsFile:
		blockIndex, resultIndex, resultSymbol, result = resultLine.strip().split('\t')
		if checkIfResultReady(result):
			count += 1
	return count


def getBlocksCount(splitEquationsFile):
	splitEquationsFile = open(splitEquationsFile, 'r')
	partIndex = 0
	lineCount = 0
	for equationLine in splitEquationsFile:
		lineCount += 1
		partIndex, equationIndex, equation = equationLine.strip().split('\t')
	if lineCount == 0:
		return 0
	else:
		return int(partIndex) + 1


if __name__ == "__main__":
	if sys.argv[1] == "HadoopSimulation":
		hadoopSimulation(sys.argv[2:])
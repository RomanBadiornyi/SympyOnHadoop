#!/usr/bin/env python3.3

import os
import sys
import subprocess
from datetime import datetime
from datetime import timedelta

from Commands import *

from Jobs.SerializeSymbols import SerializeSymbolsJob
from Jobs.SerializeEquations import SerializeEquations
from Jobs.SplitEquations import SplitEquations
from Jobs.ComputeEquations import ComputationJob
from Jobs.PrepareResults import PrepareResults
from Jobs.CalculateFinalResults import CalculateFinalResults
from Jobs.SimplifyEquations import SimplifyEquationsJob
from Jobs.MergeSimplifiedEquations import MergeSimplifiedEquations
from Jobs.MergeUndeterminedResults import MergeUndeterminedResults
from Jobs.CollectFinalResults import CollectFinalResults
from Jobs.ReplaceVariablesWithResults import ReplaceVariablesWithResults
from Jobs.MergeFinalSystemResults import MergeFinalSystemResults

Debug = False


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


def RunSymbolsSerializationJob():
	if Debug:
		job = SerializeSymbolsJob()
		job.reduce(Debug, InitInputEquationsFileName, SerializeSymbolsFileName)
	else:
		p = subprocess.Popen(SerializeSymbolsCommand.format(InitInputEquationsFileName, SerializeSymbolsFileName), shell=True)
		p.wait()


def RunEquationSerializationJob():
	if Debug:
		job = SerializeEquations()
		job.reduce(Debug, SerializeSymbolsFileName, InitInputEquationsFileName, SerializeEquationsFileName)
	else:
		p = subprocess.Popen(SerializeEquationsCommand.format(SerializeSymbolsFileName, InitInputEquationsFileName,
															  SerializeEquationsFileName), shell=True)
		p.wait()


def RunSplitEquationsJob():
	Debug=True
	operationStart = datetime.now()
	if Debug:
		job = SplitEquations()
		job.reduce(Debug, SerializeEquationsFileName, SplitEquationsFileName)
	else:
		p = subprocess.Popen(SplitEquationsCommand.format(SerializeEquationsFileName, SplitEquationsFileName), shell=True)
		p.wait()
	operationEnd = datetime.now()
	time = operationEnd - operationStart
	print("Splitting equations to blocks finished, execution time: {0}\n".format(str(time)))
	return time


def RunComputationJobs(reducersCount):
	Debug = True
	operationStart = datetime.now()
	if Debug:
		job = ComputationJob()
		for reducerNumber in range(reducersCount):
			job.reduce(reducerNumber, Debug, SplitEquationsFileName, OutputResultsFileName + str(reducerNumber))
	else:
		processesList = []
		for reducerNumber in range(reducersCount):
			p = subprocess.Popen(ComputeEquationBlockCommand.format(reducerNumber, SplitEquationsFileName,
																	OutputResultsFileName), shell=True)
			processesList.append(p)
		[p.wait() for p in processesList]

	operationEnd = datetime.now()
	time = operationEnd - operationStart
	print("Computing results in blocks finished, execution time: {0}\n".format(str(time)))
	return time


def RunCalculateFinalResultsJob():
	operationStart = datetime.now()
	if Debug:
		job = CalculateFinalResults()
		job.reduce(Debug, OutputResultsFileName + "*", PreparedResultsFileName)
	else:
		p = subprocess.Popen(CalculateFinalResultsCommand.format(OutputResultsFileName + "*", FinalResultsCountFileName),
							 shell=True)
		p.wait()
	countFile = open(FinalResultsCountFileName, "r")
	line = countFile.readline()
	finalResultsCount = int(line)
	operationEnd = datetime.now()
	time = operationEnd - operationStart
	print("Calculation of final results count finished, execution time: {0}\n".format(str(time)))
	return time, finalResultsCount


def RunPrepareResultsJob(reducersCount):
	operationStart = datetime.now()
	if Debug:
		job = PrepareResults()
		job.map(reducersCount, Debug, OutputResultsFileName + "*", PreparedResultsFileName)
	else:
		p = subprocess.Popen(PrepareResultsCommand.format(reducersCount, OutputResultsFileName + "*", PreparedResultsFileName),
							 shell=True)
		p.wait()
	operationEnd = datetime.now()
	time = operationEnd - operationStart
	print("Results prepared for simplification: {0}\n".format(str(time)))
	return time


def RunResultSimplificationJob(blocksCount):
	operationStart = datetime.now()
	if Debug:
		job = SimplifyEquationsJob()
		job.map(Debug, SplitEquationsFileName, OutputResultsFileName + "*", PreparedResultsFileName,
				ResultsForSimplificationFileName)
		for currentBlock in range(blocksCount):
			job = SimplifyEquationsJob()
			job.reduce(currentBlock, Debug, ResultsForSimplificationFileName, ResultsForSimplificationFileName + str(currentBlock))
	else:
		p = subprocess.Popen(SimplifyEquationsMapCommand.format(SplitEquationsFileName, OutputResultsFileName + "*",
														  	    PreparedResultsFileName, ResultsForSimplificationFileName),
							 shell=True)
		p.wait()
		processesList = []
		for currentBlock in range(blocksCount):
			p = subprocess.Popen(SimplifyEquationsReduceCommand.format(currentBlock, ResultsForSimplificationFileName),
								 shell=True)
			processesList.append(p)
		[p.wait() for p in processesList]
	operationEnd = datetime.now()
	time = operationEnd - operationStart
	print("Results simplification finished, execution time: {0}\n".format(str(time)))
	os.system("rm {0}".format(ResultsForSimplificationFileName))
	return time


def RunMergingSimplificationResultsJob():
	operationStart = datetime.now()
	if Debug:
		job = MergeSimplifiedEquations()
		job.map(Debug, ResultsForSimplificationFileName + "*", MergedResultsFileName)
		p = subprocess.Popen(MergeSimplifiedEquationsReduceCommand.format(MergedResultsFileName, SerializeEquationsFileName),
							 shell=True)
		p.wait()
		os.system("cp {0} {0}Copy".format(UndeterminedResultsFileName))
		job = MergeUndeterminedResults()
		job.map(Debug, ResultsForSimplificationFileName + "*", UndeterminedResultsFileName + "Copy",
				UndeterminedResultsFileName)
	else:
		p = subprocess.Popen(MergeSimplifiedEquationsMapCommand.format(ResultsForSimplificationFileName + "*",
																MergedResultsFileName),
							 shell=True)
		p.wait()
		p = subprocess.Popen(MergeSimplifiedEquationsReduceCommand.format(MergedResultsFileName, SerializeEquationsFileName),
							 shell=True)
		p.wait()
		os.system("cp {0} {0}Copy".format(UndeterminedResultsFileName))
		p = subprocess.Popen(MergeUndeterminedResultsCommand.format(ResultsForSimplificationFileName + "*",
																	UndeterminedResultsFileName + "Copy",
																	UndeterminedResultsFileName), shell=True)
		p.wait()
	os.system("rm {0}Copy".format(UndeterminedResultsFileName))
	operationEnd = datetime.now()
	time = operationEnd - operationStart
	print("Merging of simplification results finished, execution time: {0}\n".format(str(time)))
	return time


def RunReplacingResultsJob():
	operationStart = datetime.now()
	if Debug:
		os.system("cp {0} {0}Copy".format(FinalResultsFileName))
		job = CollectFinalResults()
		job.map(Debug, OutputResultsFileName + "*", FinalResultsFileName + "Copy",
				FinalResultsFileName)
		job = ReplaceVariablesWithResults()
		job.reduce(Debug, FinalResultsFileName, SerializeInitEquationsFileName, SerializeEquationsFileName)
	else:
		os.system("cp {0} {0}Copy".format(FinalResultsFileName))
		p = subprocess.Popen(CollectFinalResultsCommand.format(OutputResultsFileName + "*",
															   FinalResultsFileName + "Copy",
															   FinalResultsFileName), shell=True)
		p.wait()
		p = subprocess.Popen(ReplaceVariablesWithFinalResultsCommand.format(FinalResultsFileName,
																			SerializeInitEquationsFileName,
																			SerializeEquationsFileName), shell=True)
		p.wait()

	os.system("rm {0}Copy".format(FinalResultsFileName))
	operationEnd = datetime.now()
	time = operationEnd - operationStart
	print("Results in equations replaced: {0}\n".format(str(time)))
	return time


def RunMergingFinalSystemResultsJob():
	if Debug:
		job = MergeFinalSystemResults()
		job.reduce(Debug, FinalResultsFileName, UndeterminedResultsFileName, ResultsFileName)
	else:
		p = subprocess.Popen(MergeFinalSystemResultsCommand.format(FinalResultsFileName, UndeterminedResultsFileName,
																   ResultsFileName), shell=True)
		p.wait()


def hadoopSimulation(args):
	start = datetime.now()

	resultsCount = 0
	equationsExists = True

	SplittingToBlocksTotal = timedelta(0)
	ComputingResultsTotal = timedelta(0)
	PrepareResultsTotal = timedelta(0)
	SimplificationResultsTotal = timedelta(0)
	FinalResultsCalculationTotal = timedelta(0)
	ReplacingWithResultsTotal = timedelta(0)

	print("Start computation: {0}\n".format(str(datetime.now())))

	os.system("touch {0}".format(UndeterminedResultsFileName))
	os.system("touch {0}".format(FinalResultsFileName))

	RunSymbolsSerializationJob()
	RunEquationSerializationJob()

	os.system("cp {0} {1}".format(SerializeEquationsFileName, SerializeInitEquationsFileName))
	os.system("rm {0}".format(SerializeSymbolsFileName))

	while equationsExists:
		SplittingToBlocksTotal += RunSplitEquationsJob()
		blocksCount = HELP_FUNCTION_GET_BLOCKS_COUNT('{0}'.format(SplitEquationsFileName))

		if blocksCount == 0:
			equationsExists = False

		if not equationsExists:
			break

		ComputingResultsTotal += RunComputationJobs(blocksCount)

		time, finalResultsCount = RunCalculateFinalResultsJob()
		os.system("rm {0}".format(FinalResultsCountFileName))
		resultsCount += finalResultsCount
		FinalResultsCalculationTotal += time

		if finalResultsCount == 0:
			PrepareResultsTotal += RunPrepareResultsJob(blocksCount)
			SimplificationResultsTotal += RunResultSimplificationJob(blocksCount)
			FinalResultsCalculationTotal += RunMergingSimplificationResultsJob()
			os.system("rm {0}*".format(OutputResultsFileName))
			os.system("rm {0}*".format(ResultsForSimplificationFileName))
			os.system("rm {0}".format(PreparedResultsFileName))
			os.system("rm {0}".format(MergedResultsFileName))
			os.system("rm {0}".format(SplitEquationsFileName))
		else:
			ReplacingWithResultsTotal += RunReplacingResultsJob()
			os.system("rm {0}*".format(OutputResultsFileName))
			os.system("rm {0}".format(SplitEquationsFileName))
	RunMergingFinalSystemResultsJob()
	os.system("rm {0}".format(SerializeInitEquationsFileName))
	os.system("rm {0}".format(UndeterminedResultsFileName))
	os.system("rm {0}".format(SerializeEquationsFileName))
	os.system("rm {0}".format(SplitEquationsFileName))
	os.system("rm {0}".format(FinalResultsFileName))

	end = datetime.now()
	print('Execution time is: {0}'.format(str(end - start)))
	totalLabel = 'Total execution time is:'
	print('{0}, {1} {2}'.format("Splitting to block operation", totalLabel, SplittingToBlocksTotal))
	print('{0}, {1} {2}'.format("Computing results operation", totalLabel, ComputingResultsTotal))
	print('{0}, {1} {2}'.format("Preparing results for simplification operation", totalLabel, PrepareResultsTotal))
	print('{0}, {1} {2}'.format("Results simplification operation", totalLabel, SimplificationResultsTotal))
	print('{0}, {1} {2}'.format("Analyze simplified results operation", totalLabel, FinalResultsCalculationTotal))
	print('{0}, {1} {2}'.format("Replacing variables with results operation", totalLabel, ReplacingWithResultsTotal))


if __name__ == "__main__":
	if sys.argv[1] == "HadoopSimulation":
		hadoopSimulation(sys.argv[2:])
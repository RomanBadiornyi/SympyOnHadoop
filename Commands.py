SerializeSymbolsCommand = "cat {0} | sort -k1,1 -n | python3.3 Jobs/SerializeSymbols.py reduce | cat > {1}"
SerializeEquationsCommand = "cat {0} {1} | sort -k1,1 -n | python3.3 Jobs/SerializeEquations.py reduce | cat > {2}"
SplitEquationsCommand = "cat {0} | python3.3 Jobs/SplitEquations.py reduce | cat > {1}"
ComputeEquationBlockCommand = "cat {1} | grep -P '^{0}\t' | python3.3 Jobs/ComputeEquations.py reduce {0} | cat > {2}{0}"
PrepareResultsCommand = "cat {1} | python3.3 Jobs/PrepareResults.py map {0} | cat > {2}"
CalculateFinalResultsCommand = "cat {0} | python3.3 Jobs/CalculateFinalResults.py reduce | cat > {1}"
SimplifyEquationsMapCommand = "cat {0} {1} {2} | python3.3 Jobs/SimplifyEquations.py map | cat > {3}"
SimplifyEquationsReduceCommand = "cat {1} | grep -P '^{0}\t' | sort -k1,1 -n -k2,2 -n -k3,3 -n | python3.3 Jobs/SimplifyEquations.py reduce {0} | cat > {1}{0}"
MergeSimplifiedEquationsMapCommand = "cat {0} | python3.3 Jobs/MergeSimplifiedEquations.py map | cat > {1}"
MergeSimplifiedEquationsReduceCommand = "cat {0} | sort -k1,1 -n | cat > {1}"
MergeUndeterminedResultsCommand = "cat {0} {1} | python3.3 Jobs/MergeUndeterminedResults.py map | cat > {2}"
CollectFinalResultsCommand = "cat {0} {1} | python3.3 Jobs/CollectFinalResults.py map | cat > {2}"
ReplaceVariablesWithFinalResultsCommand = "cat {0} {1} | sort -k1,1 -n | python3.3 Jobs/ReplaceVariablesWithResults.py reduce | cat > {2}"
MergeFinalSystemResultsCommand = "cat {0} {1} | sort -k1,1 -n | python3.3 Jobs/MergeFinalSystemResults.py reduce | cat > {2}"

InitInputEquationsFileName = "InitInputEquations"
SerializeSymbolsFileName = "SerializedSymbols"
SerializeInitEquationsFileName = "SerializedInitEquations"
SerializeEquationsFileName = "SerializedEquations"
SplitEquationsFileName = "SplitEquations"
OutputResultsFileName = "OutputResults"
PreparedResultsFileName = "PreparedResults"
FinalResultsCountFileName = "FinalResultsCount"
ResultsForSimplificationFileName = "ResultsForSimplification"
MergedResultsFileName = "MergedResults"
UndeterminedResultsFileName = "UndeterminedResults"
FinalResultsFileName = "FinalResults"
ResultsFileName = "Results"
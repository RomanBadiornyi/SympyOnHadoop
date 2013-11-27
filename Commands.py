MapInitDataCommand = 'cat InitInputEquations | sort -k1,1 -n | python3.3 Jobs/LoadInitDataJob.py reduce | sort -k1,1 -n | cat > InputEquations'
SplitEquationsCommand = "cat InputEquations | python3.3 Jobs/ComputationJob.py map | sort -k1,1 -k2,2 -n | cat > InputEquationsSplit"
ComputeEquationBlockCommand = "cat InputEquationsSplit | grep -P '^{0}\t' | python3.3 Jobs/ComputationJob.py reduce | sort | cat > OutputResults{0}"
MergeResultsCommand = "cat OutputResults* | python3.3 Jobs/MergeResultsJob.py reduce | sort -n | cat > MergedResults"
MapResultsForSimplificationCommand = "cat MergedResults | python3.3 Jobs/MergeResultsForSimplificationJob.py reduce {0} | cat > ResultsForSimplification"
JoinResultsWithEquationsCommand = "cat MergedResults InputEquationsSplit | sort -k1,1 -n | python3.3 Jobs/JoinResultsWithEquationsJob.py map | sort -k1,2 -n | python3.3 Jobs/JoinResultsWithEquationsJob.py reduce | cat > EquationsWithResults"
JoinEquationsWithResultForSimplificationCommand = "cat EquationsWithResults ResultsForSimplification | sort -k1,1 -n | python3.3 Jobs/JoinEquationsWithResultForSimplificationJob.py map | sort -k1,1 -n | python3.3 Jobs/JoinEquationsWithResultForSimplificationJob.py reduce | cat > EquationsWithResultsForSimplification"
SimplifyEquationsCommand = "cat EquationsWithResultsForSimplification | grep -P '^{0}\t' | sort -k1,1 -n -k2,2 -n | python3.3 Jobs/SimplifyEquationsJob.py reduce | cat > SimplificationResult{0}"
MergeSimplificationResultsToInputEquationsCommand = "cat SimplificationResult* | python3.3 Jobs/MergeSimplificationEquationsJob.py reduce | sort -k1,1 -n | cat > InputEquations"
MergeSimplificationResultsToUndeterminedResults = "cat SimplificationResult* UndeterminedResultsCopy | python3.3 Jobs/MergeSimplificationUndeterminedResultsJob.py reduce | sort -k1,1 -n | cat > UndeterminedResults"
CollectFinalResultsCommand = "cat MergedResults FinalResultsCopy | python3.3 Jobs/CollectFinalResultsJob.py reduce | cat > FinalResults"
ReplaceVariablesWithFinalResultsCommand = "cat FinalResults InitInputEquations | sort -k1,1 -n | python3.3 Jobs/ReplaceVariablesWithResultsJob.py reduce | cat > InputEquations"
MergeFinalSystemResultsCommand = "cat FinalResults UndeterminedResults | sort -k2,2 -n | python3.3 Jobs/MergeFinalSystemResultsJob.py reduce | cat > Results"

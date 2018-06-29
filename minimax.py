import copy
import itertools

class SimplifyMiniMax:
    """
    DOT 2018-06-29:
    
    Standard MiniMax algorithm. With this approach, simplification
    is thought of as a zero sum game of two players. The algorithm
    tries to MAXIMIZE the measure before each new rule application, while
    expectig the worst possible scenario for the given rule application.
    """
    def __init__(self, expression, rules, iterations, eps, transformations, ruleApplication, measure):
        """
        DOT 2018-06-29:
        
        Initalize internal states
        """
        self._rules = rules
        self._transformations = transformations
        self._applyRule = ruleApplication
        self._measure = measure
        self._root = expression
        self._iterations = iterations
        self._eps = eps
    
    def NormalizeNode(self):
        """
        DOT 2018-06-29:
        
        Normalizes the root node for further simplification. This means
        the method applies all available transformations
        """
        for trf in self._transformations:
            self._root = trf(copy.deepcopy(self._root))
    
    def GetNextMove(self):
        """
        DOT 2018-06-29:
        
        Decide the next rule to apply during simplification. This method
        implements a single MiniMax iteration. Current implementation looks
        ahead three possible moves. Keep in mind, that increasing this number
        greatly effects performance. 
        """
        self.NormalizeNode()
        
        firstLevelExpressions = []
        secondLevelExpressions = []
        thirdLevelExpressions = []
        
        secondLevelScores = []
        firstLevelScores = []
        
        #Generate possible next moves
        for rule in self._rules:
            firstLevelExpressions.append(self._applyRule(rule, copy.deepcopy(self._root)))
            firstLevelScores.append(None)

        #Generate possible second level moves
        for expr in firstLevelExpressions:
            secondLevelExpressions.append([])
            secondLevelScores.append([])
            for rule in self._rules:
                secondLevelExpressions[-1].append(self._applyRule(rule, copy.deepcopy(expr)))
                secondLevelScores[-1].append(None)

        #Generate third level moves
        for flexpr in secondLevelExpressions:
            thirdLevelExpressions.append([])
            for expr in flexpr:
                thirdLevelExpressions[-1].append([])
                for rule in self._rules:
                    thirdLevelExpressions[-1][-1].append(self._applyRule(rule, copy.deepcopy(expr)))
                    
        #First generate the second level scores from the third level expressions
        for i in range(0, len(thirdLevelExpressions)):
            for j in range(0, len(thirdLevelExpressions[i])):
                candidates = [self._measure(expr) for expr in thirdLevelExpressions[i][j]]
                secondLevelScores[i][j] = min(candidates)
            
        #Finally, generate the firs level scores from the second level scores
        for i in range(0, len(secondLevelExpressions)):
            firstLevelScores[i] = max(secondLevelScores[i])
        
        #New expression:
        self._root = firstLevelExpressions[firstLevelScores.index(max(firstLevelScores))]
        self.NormalizeNode()
        
    def MiniMax(self):
        """
        DOT 2018-06-29:
        
        Iteratively run minimax steps, until the measure of the new expression
        is greater than self._eps, or the maximum number of iterations is reached
        """
        self.NormalizeNode()
        currentIteration = 0
        
        print("Minimax begin")
        print("max iterations: "+str(self._iterations))
        print("eps: "+str(self._eps))
        
        while self._measure(self._root) < self._eps and currentIteration < self._iterations:
            print("[MiniMax] iteration: "+str(currentIteration)+" expression: "+str(self._root)+" measure: "+str(self._measure(self._root)))
            self.GetNextMove()
            currentIteration += 1
            
        print("Minimax end")
            
"""
Examples of usage. (Just copy and paste to the end of simplify.py)

1. m2 -> the longer the expression, the higher the score, final evaulation will be: (((sin((1*a))*cos((1*a)))*cos((2*a)))+(sin((1*b))*cos((1*b))))
print("*************** MINIMAX METHOD ****************")
Simplifier = minimax.SimplifyMiniMax(expr, [sin_rule, one_rule], 5, 100, [eval_tree], apply_rule_in_tree, m2)
Simplifier.MiniMax()

2. m -> the shorter the expression, the higher the score, therefore original expression will not change
print("*************** MINIMAX METHOD ****************")
Simplifier = minimax.SimplifyMiniMax(expr, [sin_rule, one_rule], 5, 100, [eval_tree], apply_rule_in_tree, m)
Simplifier.MiniMax()

"""     

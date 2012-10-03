"""
Performs verification testing for the algorithm
for finding and representing correlated equilibria.

Author - Chris Ratcliff

"""

from gambit.lib.libgambit import *
from numpy import *
from random import *
from os import *
from matplotlib.nxutils import pnpoly

import CorrEq

def deriveConstraints(game):
    
    constraints = []
    
    for p in range(2): # player
        
        for s in range(len(game.players[p].strategies)):
            for alt_s in range(len(game.players[p].strategies)):
                
                if s == alt_s:
                    continue
                
                constraint = [None for i in range(len(game.contingencies))]
                
                for t in range(len(game.players[not p].strategies)):
                    
                    if p == 0:
                        index = CorrEq.contingencyToIndex((s,t),len(game.players[1].strategies))
                        assert(constraint[index] == None)
                        constraint[index] = float(game._get_contingency(s,t)[p]) - float(game._get_contingency(alt_s,t)[p])

                    else:
                        index = CorrEq.contingencyToIndex((t,s),len(game.players[1].strategies))
                        assert(constraint[index] == None)
                        constraint[index] = float(game._get_contingency(t,s)[p]) - float(game._get_contingency(t,alt_s)[p])
                
                constraint = [0 if i==None else i for i in constraint]
                constraints.append(constraint)
                
    return constraints


def testGame(file_path):

    TEST_CASES = 100
    
    game = gambit.read_game(file_path)

    vertices,edges = CorrEq.findPolygon(game)
    edges = CorrEq.removeExtraEdges(vertices,edges)

    constraints = deriveConstraints(game)

    points = CorrEq.orderVertices(edges)

    if points == None:
        points = vertices
    
    for i in range(TEST_CASES):
        # Pick a random probability distribution
        probs = [random() for j in range(len(game.contingencies))]       
        # Ensure probabilities sum to 1
        probs = [j/sum(probs) for j in probs]
        
        # Determine whether the distribution is a correlated equilibrium
            # It is if it satisfies the constraints in the LP       
        is_corr_eq = True
        
        for j in constraints:
            if sum(multiply(probs,j)) < 0:
                is_corr_eq = False
                break
        
        u1,u2 = CorrEq.probsToUtilities(probs, game)
        inside = pnpoly(u1,u2,points)
        
        if is_corr_eq == True and inside == False:
            raise Exception('Test failed on: ' + file_path)
            print 'Test failed on: ' + file_path
                  
        
def main():
    
    path = 'test_games/'
    listing = listdir(path)
    
    for file in listing:
        print path+file
        testGame(path+file)
        
    return 0

if __name__ == '__main__':
    main()
    
# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import capture
import random, time, util
from game import Directions
import game
from util import nearestPoint
#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

"""
Zhenyuan : I wrote three functions here
"""
tunnels = []
def getAllTunnels(legalPositions):
    tunnels = []
    while len(tunnels) != len(getMoreTunnels(legalPositions)):
        tunnels = getMoreTunnels(legalPositions)
    return tunnels

def getMoreTunnels(legalPositions):
    tunnels = []
    for i in legalPositions:
        neighborTunnelsNum = getSuccsorsNum(i, tunnels)
        succsorsNum = getSuccsorsNum(i, legalPositions)
        if succsorsNum - neighborTunnelsNum == 1:
            tunnels.append(i)
    return tunnels

def getSuccsorsNum(pos, legalPositions):
    num = 0
    x, y = pos
    if (x + 1, y) in legalPositions:
        num += 1
    if (x - 1, y) in legalPositions:
        num += 1
    if (x, y + 1) in legalPositions:
        num += 1
    if (x, y - 1) in legalPositions:
        num += 1
    return num

class ReflexCaptureAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.

    '''

    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)


    '''
    Your initialization code goes here, if you need any.
    '''
    """
    Zhenyuan : global variable tunnels here
    """
    global tunnels
    if len(tunnels) == 0:
      legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 1]
      tunnels = getAllTunnels(legalPositions)

    '''
    Your initialization code goes here, if you need any.
    '''

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """

    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    Q = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == Q]

    foodLeft = len(self.getFood(gameState).asList())
    action = random.choice(bestActions)
    if foodLeft <= 2:
        bestDist = 9999
        for action in actions:
            successor = self.getSuccessor(gameState, action)
            pos2 = successor.getAgentPosition(self.index)
            dist = self.getMazeDistance(self.start, pos2)
            if dist < bestDist:
                bestAction = action
                bestDist = dist
        return bestAction

    return action

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights


  def distMyAgents(self, successor):
    agent1, agent2 = self.getTeam(successor)
    dist1 = successor.getAgentState(agent1).getPosition()
    dist2 = successor.getAgentState(agent2).getPosition()
    return self.getMazeDistance(dist1,dist2)

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    myPos = successor.getAgentState(self.index).getPosition()
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghost = [a for a in enemies if not a.isPacman and a.getPosition() is not None]
    scaredGhost = [a for a in ghost if a.scaredTimer > 0]
    activeGhost = [a for a in ghost if a not in scaredGhost]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
    foodList = self.getFood(successor).asList()
    myAgentsDist = self.distMyAgents(successor)
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    capsule = self.getCapsules(gameState)

    features['closestFood'] = minDistance
    if myPos in self.getFood(gameState).asList():
        features['closestFood'] = 0

    features['successorScore'] = self.getScore(successor)

    if len(capsule) != 0:
        features['distanceToCapsule'] = self.getMazeDistance(myPos, capsule[0])

    if action == Directions.STOP: features['stop'] = 1

    if len(activeGhost) > 0:
        dists = min([self.getMazeDistance(myPos, a.getPosition()) for a in activeGhost])
        features['distToGhost'] = dists
        features['inverseDist'] = 1/dists
        features['numOfGhostNearby'] = len(activeGhost)
        if myPos in tunnels and dists < 4:
            features['inTunnel'] = 1

    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'closestFood':  -2, 'successorScore': 800,  'distanceToCapsule': -40, 'stop':-1000,
        'numOfGhostNearby': -30,'distToGhost': 50, 'inverseDist': -20, 'inTunnel': -500}




class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    myCapsule = self.getCapsulesYouAreDefending(gameState)

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
        dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)
    
    if len(invaders) > 0 and len(myCapsule) != 0:
        dist1 = [self.getMazeDistance(myCapsule[0], a.getPosition()) for a in invaders]
        dist2 = self.getMazeDistance(myCapsule[0], myPos)
        features['protectCapsules'] = dist2 - min(dist1)


    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1
    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -100, 'stop': -100, 'reverse': -2, 'protectCapsules': 80}



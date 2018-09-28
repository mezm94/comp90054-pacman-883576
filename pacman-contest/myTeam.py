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
walls = []

def getAllTunnels(legalPositions):
    tunnels = []
    while len(tunnels) != len(getMoreTunnels(legalPositions, tunnels)):
        tunnels = getMoreTunnels(legalPositions, tunnels)
    return tunnels

def getMoreTunnels(legalPositions, tunnels):
    newTunnels = tunnels
    for i in legalPositions:
        neighborTunnelsNum = getSuccsorsNum(i, tunnels)
        succsorsNum = getSuccsorsNum(i, legalPositions)
        if succsorsNum - neighborTunnelsNum == 1 and i not in tunnels:
            newTunnels.append(i)
    return newTunnels

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

def getSuccsorsPos(pos, legalPositions):
    succsorsPos = []
    x, y = pos
    if (x + 1, y) in legalPositions:
        succsorsPos.append((x + 1, y))
    if (x - 1, y) in legalPositions:
        succsorsPos.append((x - 1, y))
    if (x, y + 1) in legalPositions:
        succsorsPos.append((x, y + 1))
    if (x, y - 1) in legalPositions:
        succsorsPos.append((x, y - 1))
    return succsorsPos

def nextPos(pos, action):
  x, y = pos
  if action == Directions.NORTH:
    return (x, y + 1)
  if action == Directions.SOUTH:
    return (x, y - 1)
  if action == Directions.EAST:
    return (x + 1, y)
  if action == Directions.WEST:
    return (x - 1, y)
  return pos

def manhattanDist((x1,y1),(x2,y2)):
   return x2-x1+y2-y1


def getPossibleEntry(pos, tunnels, legalPositions):
    x, y = pos
    if (x + 1, y) in legalPositions and (x + 1, y) not in tunnels:
        return (x + 1, y)
    if (x - 1, y) in legalPositions and (x - 1, y) not in tunnels:
        return (x - 1, y)
    if (x, y + 1) in legalPositions and (x, y + 1) not in tunnels:
        return (x, y + 1)
    if (x, y - 1) in legalPositions and (x, y - 1) not in tunnels:
        return (x, y - 1)
    return None


def getATunnel(pos, tunnels):

    if pos not in tunnels:
        return None

    bfs_queue = util.Queue()
    closed = []
    bfs_queue.push(pos)

    while not bfs_queue.isEmpty():
        currPos = bfs_queue.pop()

        if currPos not in closed:
            closed.append(currPos)
            succssorsPos = getSuccsorsPos(currPos, tunnels)
            for i in succssorsPos:
                if i not in closed:
                    bfs_queue.push(i)

    return closed


def getTunnelEntry(pos, tunnels, legalPositions):
    if pos not in tunnels:
        return None
    aTunnel = getATunnel(pos, tunnels)
    for i in aTunnel:
        possibleEntry = getPossibleEntry(i, tunnels, legalPositions)
        if possibleEntry != None:
            return possibleEntry


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
    self.tunnelEntry = None
    global walls 
    global tunnels
    global openRoad
    global legalPositions
    walls = gameState.getWalls().asList()
    if len(tunnels) == 0:
      legalPositions = [p for p in gameState.getWalls().asList(False)]
      tunnels = getAllTunnels(legalPositions)
      openRoad = list(set(legalPositions).difference(set(tunnels)))



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

  def ifWasteTunnel(self, gameState, successor):
    '''
    xueyang Ding, check if a tunnel is useless (no food inside)
    '''
    curPos = gameState.getAgentState(self.index).getPosition()
    sucPos = successor.getAgentState(self.index).getPosition()
    if curPos not in tunnels and sucPos in tunnels:

      self.tunnelEntry = curPos

      dfs_stack = util.Stack()
      closed = []
      dfs_stack.push((sucPos, 1))

      while not dfs_stack.isEmpty():
        (x, y), length = dfs_stack.pop()
        if self.getFood(gameState)[int(x)][int(y)]:
          return length

        if (x, y) not in closed:
          closed.append((x, y))
          succssorsPos = getSuccsorsPos((x, y), tunnels)
          for i in succssorsPos:
            if i not in closed:
              nextLength = length + 1
              dfs_stack.push((i, nextLength))
    return 0

  def getTunnelFood(self, gameState):
      '''
      Zhenyuan : get the closest food in tunnel if in tunnel
      '''

      curPos = gameState.getAgentState(self.index).getPosition()
      bfs_queue = util.Queue()
      closed = []
      bfs_queue.push(curPos)

      while not bfs_queue.isEmpty():
          x, y = bfs_queue.pop()
          if self.getFood(gameState)[int(x)][int(y)]:
              return (x, y)

          if (x, y) not in closed:
              closed.append((x, y))
              succssorsPos = getSuccsorsPos((x, y), tunnels)
              for i in succssorsPos:
                  if i not in closed:
                      bfs_queue.push(i)

      return None


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
    curPos = gameState.getAgentState(self.index).getPosition()
    myPos = successor.getAgentState(self.index).getPosition()
    nextPosition = nextPos(curPos,action)
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghost = [a for a in enemies if not a.isPacman and a.getPosition() is not None and manhattanDist(curPos,a.getPosition()) <= 5]
    scaredGhost = [a for a in ghost if a.scaredTimer > 0]
    activeGhost = [a for a in ghost if a not in scaredGhost]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
    foodList = self.getFood(successor).asList()
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
    capsule = self.getCapsules(gameState)
    checkTunnel = self.ifWasteTunnel(gameState, successor)

    if self.getTimeLeft(gameState)/4 < self.getLengthToHome(gameState) + 3:
        features['distToHome'] = self.getLengthToHome(successor)

    features['closestFood'] = minDistance
    if myPos in self.getFood(gameState).asList():
        features['closestFood'] = 0

    features['successorScore'] = self.getScore(successor)

    if len(activeGhost) > 0 and len(capsule) != 0 and self.getMazeDistance(curPos, capsule[0]) < 8:
        if self.getMazeDistance(curPos, capsule[0]) < min([self.getMazeDistance(capsule[0], a.getPosition()) for a in activeGhost]):
          features['distanceToCapsule'] = 8 - self.getMazeDistance(myPos, capsule[0])
          if myPos in capsule:
              features['distanceToCapsule'] = 8


    if action == Directions.STOP: features['stop'] = 1

    if len(activeGhost) > 0:
        dists = min([self.getMazeDistance(myPos, a.getPosition()) for a in activeGhost])
        features['distToGhost'] = dists
        ghostPos = [a.getPosition() for a in activeGhost]
        if nextPosition in ghostPos:
            features['die'] = 1

    if successor.getAgentState(self.index).isPacman and curPos not in tunnels and \
        successor.getAgentState(self.index).getPosition() in tunnels and checkTunnel == 0:
        features['wasteAction'] = -1
        
    if len(activeGhost) > 0:
         dist = min([self.getMazeDistance(curPos, a.getPosition()) for a in activeGhost])
         if checkTunnel != 0 and checkTunnel*2 >= dist-2:
             features['wasteAction'] = -1

    if curPos in tunnels and len(activeGhost) > 0:
        foodPos = self.getTunnelFood(gameState)
        if foodPos == None:
            features['escapeTunnel'] = self.getMazeDistance(myPos, self.tunnelEntry)
        else:
            lengthToEscape = self.getMazeDistance(myPos, foodPos) + self.getMazeDistance(foodPos, self.tunnelEntry)
            ghostToEntry = min([self.getMazeDistance(self.tunnelEntry, a.getPosition()) for a in activeGhost])
            if ghostToEntry - lengthToEscape == 1 and len(scaredGhost) == 0:
                features['escapeTunnel'] = self.getMazeDistance(myPos, self.tunnelEntry)

    if curPos in tunnels and len(scaredGhost) > 0:
        foodPos = self.getTunnelFood(gameState)
        if foodPos == None:
            features['escapeTunnel'] = self.getMazeDistance(myPos, self.tunnelEntry)
        else:
            lengthToEscape = self.getMazeDistance(myPos, foodPos) + self.getMazeDistance(foodPos, self.tunnelEntry)
            if len(scaredGhost) != 0 and scaredGhost[0].scaredTimer - lengthToEscape == 1:
                features['escapeTunnel'] = self.getMazeDistance(myPos, self.tunnelEntry)

    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'closestFood':  -2, 'distToHome':-10,'successorScore': 800,  'distanceToCapsule': 4000, 'stop':-1000,
        'distToGhost': 50, 'wasteAction': 2000,'escapeTunnel':-3000,'die':-10000}

  def getLengthToHome(self, gameState):
      curPos = gameState.getAgentState(self.index).getPosition()
      width = gameState.data.layout.width
      height = gameState.data.layout.height
      legalPositions = [p for p in gameState.getWalls().asList(False)]
      legalRed = [p for p in legalPositions if p[0] == width / 2]
      legalBlue = [p for p in legalPositions if p[0] == width / 2 + 1]
      if self.red:
          return min([self.getMazeDistance(curPos, a) for a in legalRed])
      else:
          return min([self.getMazeDistance(curPos, a) for a in legalBlue])

  def getTimeLeft(self, gameState):
      return gameState.data.timeleft

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
    curPos = gameState.getAgentState(self.index).getPosition()
    curState = gameState.getAgentState(self.index)
    sucState = successor.getAgentState(self.index)
    sucPos = sucState.getPosition()
    curCapsule = self.getCapsulesYouAreDefending(gameState)

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 100
    if sucState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    curEnemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    curInvaders = [a for a in curEnemies if a.isPacman and a.getPosition() != None]


    if self.ifNeedsBlockTunnel(curInvaders, curPos, curCapsule) and curState.scaredTimer == 0:
        features['runToTunnelEntry'] = self.getMazeDistance(getTunnelEntry(curInvaders[0].getPosition(),tunnels,legalPositions),sucPos)
        return features

    if curPos in tunnels and len(curInvaders) == 0 and nextPos == getTunnelEntry(curPos, tunnels, legalPositions):
        features['leaveTunnel'] = 1
        print features


    features['numInvaders'] = len(invaders)        
    if len(curInvaders) == 0 and not successor.getAgentState(self.index).isPacman and curState.scaredTimer == 0:
        if  curPos not in tunnels and successor.getAgentState(self.index).getPosition() in tunnels: 
            features['wasteAction'] = -1


    if len(invaders) > 0 and curState.scaredTimer == 0:            
        dists = [self.getMazeDistance(sucPos, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)
    
    if len(invaders) > 0 and curState.scaredTimer != 0:           
        dists = min([self.getMazeDistance(sucPos, a.getPosition()) for a in invaders])
        features['followMode'] = (dists-2)*(dists-2)
        if curPos not in tunnels and successor.getAgentState(self.index).getPosition() in tunnels:
            features['wasteAction'] = -1

    if len(invaders) > 0 and len(curCapsule) != 0:         
        dist1 = [self.getMazeDistance(curCapsule[0], a.getPosition()) for a in invaders]
        dist2 = self.getMazeDistance(curCapsule[0], sucPos)
        features['protectCapsules'] = dist2 - min(dist1)


    if action == Directions.STOP: features['stop'] = 1        
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1              
    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -100, 'stop': -1000, 'reverse': -2, 'protectCapsules': 80, 'wasteAction':2000,'followMode':-1000, 'runToTunnelEntry': -1, 'leaveTunnel':-100}

  
  def ifNeedsBlockTunnel(self, curInvaders, currentPostion, curCapsule): 
    if len(curInvaders) == 1:
      invadersPos = curInvaders[0].getPosition()
      if invadersPos in tunnels:
        tunnelEntry = getTunnelEntry(invadersPos, tunnels, legalPositions)
        if self.getMazeDistance(tunnelEntry,currentPostion) <= self.getMazeDistance(tunnelEntry,invadersPos) and curCapsule not in getATunnel(invadersPos,tunnels):
           return True
    return False
  






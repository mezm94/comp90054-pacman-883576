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
import math
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
defensiveTunnels = []
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

def manhattanDist(pos1,pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x2-x1) + abs(y2-y1)


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


class Node:
    def __init__(self, value, id=0):
        (gameState, t, n) = value
        self.id = id
        self.children = []
        self.value = (gameState, float(t), float(n))
        self.isLeaf = True

    def addChild(self, child):
        self.children.append(child)

    def chooseChild(self):
        _, _, pn = self.value
        maxUCB = -999999
        bestChild = None
        for i in self.children:
            _, t, n = i.value
            if n == 0:
                return i
            UCB = t + 1.96 * math.sqrt(math.log(pn) / n)
            if maxUCB < UCB:
                maxUCB = UCB
                bestChild = i
        return bestChild

    def findParent(self, node):
        for i in self.children:
            if i == node:
                return self
            else:
                possibleParent = i.findParent(node)
                if possibleParent != None:
                    return possibleParent

    def __str__(self):
        (_, t, n) = self.value
        id = self.id
        return "Node " + str(id) + ", t = " + str(t) + ", n = " + str(n)


class Tree:
    def __init__(self, root):
        self.count = 1
        self.tree = root
        self.leaf = [root.value[0]]

    def insert(self, parent, child):
        id = self.count
        self.count += 1
        child.id = id
        parent.addChild(child)
        if parent.value[0] in self.leaf:
            self.leaf.remove(parent.value[0])
        parent.isLeaf = False
        self.leaf.append(child.value[0])

    def getParent(self, node):
        if node == self.tree:
            return None
        return self.tree.findParent(node)

    def backPropagate(self, r, node):
        (gameState, t, n) = node.value
        node.value = (gameState, t + r, n + 1)
        parent = self.getParent(node)
        if parent != None:
            self.backPropagate(r, parent)

    def select(self, node = None):
        if node == None:
            node = self.tree
        if not node.isLeaf:
            nextNode = node.chooseChild()
            return self.select(nextNode)
        else:
            return node

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
    self.debugDraw(defensiveTunnels, [0.5,0.5,0])
    """
    self.changeEntrance = False
    self.nextEntrance = None
    self.carriedDot = 0
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
    self.capsule = None
    self.nextOpenFood = None
    self.nextTunnelFood = None
    self.runToBoundary = None
    self.stuckStep = 0
    self.curLostFood = None
    self.ifStuck = False
    global defensiveTunnels
    width = gameState.data.layout.width
    legalRed = [p for p in legalPositions if p[0] < width / 2]
    legalBlue = [p for p in legalPositions if p[0] >= width / 2]

    if len(defensiveTunnels) == 0:
        if self.red:
            defensiveTunnels = getAllTunnels(legalRed)
        else:
            defensiveTunnels = getAllTunnels(legalBlue)


  def chooseAction(self, gameState):

    actions = gameState.getLegalActions(self.index)

    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    Q = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == Q]

    if self.ifStuck:
        node = Node(gameState, 0, 0)
        tree = Tree(node)
        return self.simulation(tree)

    action = random.choice(bestActions)

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
    '''
    if self.index == 0:
        print action,features,features*weights
        print gameState
    '''
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

  def getTimeLeft(self, gameState):
      return gameState.data.timeleft

  def getEntrance(self,gameState):
        width = gameState.data.layout.width
        height = gameState.data.layout.height
        legalPositions = [p for p in gameState.getWalls().asList(False)]
        legalRed = [p for p in legalPositions if p[0] == width / 2 - 1]
        legalBlue = [p for p in legalPositions if p[0] == width / 2]
        redEntrance = []
        blueEntrance = []
        for i in legalRed:
            for j in legalBlue:
                if i[0] + 1 == j[0] and i[1] == j[1]:
                    redEntrance.append(i)
                    blueEntrance.append(j)
        if self.red:
            return redEntrance
        else:
            return blueEntrance


class OffensiveReflexAgent(ReflexCaptureAgent):


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
    scaredGhost = [a for a in ghost if a.scaredTimer > 1]
    activeGhost = [a for a in ghost if a not in scaredGhost]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() is not None]
    currentFoodList = self.getFood(gameState).asList()
    allFoodList = self.getFood(gameState).asList()
    openRoadFood = [a for a in allFoodList if a not in tunnels]
    tunnelFood = [a for a in allFoodList if a in tunnels]
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    capsule = self.getCapsules(gameState)
    checkTunnel = self.ifWasteTunnel(gameState, successor)

    features['successorScore'] = self.getScore(successor)

    if len(ghost) == 0:
        self.capsule = None
        self.nextOpenFood = None
        self.nextTunnelFood = None

    if gameState.getAgentState(self.index).isPacman:
        self.changeEntrance = False

    if nextPosition in currentFoodList:
        self.carriedDot += 1
    if not gameState.getAgentState(self.index).isPacman:
        self.carriedDot = 0

    if self.getTimeLeft(gameState)/4 < self.getLengthToHome(gameState) + 3:
        features['distToHome'] = self.getLengthToHome(successor)
        return features

    if len(activeGhost) == 0 and len(allFoodList) != 0 and len(currentFoodList) >= 3:
      features['safeFoodDist'] = min([self.getMazeDistance(myPos, food) for food in allFoodList])
      if myPos in self.getFood(gameState).asList():
          features['safeFoodDist'] = -1
    if len(currentFoodList) < 3:
      features['return'] = self.getLengthToHome(successor)

    if len(activeGhost) > 0 and len(currentFoodList) >= 3:                                    
        dists = min([self.getMazeDistance(myPos, a.getPosition()) for a in activeGhost])
        features['distToGhost'] = 100 - dists
        ghostPos = [a.getPosition() for a in activeGhost]
        if nextPosition in ghostPos:
            features['die'] = 1
        if nextPosition in [getSuccsorsPos(p,legalPositions) for p in ghostPos][0]:
            features['die'] = 1
        if len(openRoadFood) > 0:             
            features['openRoadFood'] = min([self.getMazeDistance(myPos, food) for food in openRoadFood])
            if myPos in openRoadFood:
              features['openRoadFood'] = -1
        elif len(openRoadFood) == 0:
            features['return'] = self.getLengthToHome(successor)
          
    if len(activeGhost) > 0 and len(currentFoodList) >= 3:
        if len(openRoadFood) > 0:
            safeFood = []
            for food in openRoadFood:
                if self.getMazeDistance(curPos, food) < min([self.getMazeDistance(a.getPosition(), food) for a in activeGhost]):
                    safeFood.append(food)
            if len(safeFood) != 0:
                closestSFdist = min([self.getMazeDistance(curPos, food) for food in safeFood])
                for food in safeFood:
                    if self.getMazeDistance(curPos, food) == closestSFdist:
                        self.nextOpenFood = food
                        break

    if len(activeGhost) > 0 and len(tunnelFood) > 0 and len(scaredGhost) == 0 and len(currentFoodList) >= 3:
        minTFDist = min([self.getMazeDistance(curPos, tf) for tf in tunnelFood])
        safeTfood = []
        for tf in tunnelFood:
            tunnelEntry = getTunnelEntry(tf,tunnels,legalPositions)
            if self.getMazeDistance(curPos, tf) + self.getMazeDistance(tf, tunnelEntry) < min([self.getMazeDistance(a.getPosition(), tunnelEntry) for a in activeGhost]):
                safeTfood.append(tf)
        if len(safeTfood) > 0:
            closestTFdist = min([self.getMazeDistance(curPos, food) for food in safeTfood])
            for food in safeTfood:
                if self.getMazeDistance(curPos, food) == closestTFdist:
                    self.nextTunnelFood = food
                    break

    if self.nextOpenFood != None:
        features['goToSafeFood'] = self.getMazeDistance(myPos, self.nextOpenFood)
        if myPos == self.nextOpenFood:
            features['goToSafeFood'] = -0.0001
            self.nextOpenFood = None

    if features['goToSafeFood'] == 0 and self.nextTunnelFood != None:
        features['goToSafeFood'] = self.getMazeDistance(myPos, self.nextTunnelFood)
        if myPos == self.nextTunnelFood:
            features['goToSafeFood'] = 0
            self.nextTunnelFood = None

    if len(activeGhost) > 0 and len(capsule) != 0:
        for c in capsule:
            if self.getMazeDistance(curPos, c) < min([self.getMazeDistance(c, a.getPosition()) for a in activeGhost]):
                self.capsule = c

    if len(scaredGhost) > 0 and len(capsule) != 0:
        for c in capsule:
            if self.getMazeDistance(curPos, c) >= scaredGhost[0].scaredTimer and self.getMazeDistance(curPos, c) < min([self.getMazeDistance(c, a.getPosition()) for a in scaredGhost]):
                self.capsule = c

    if curPos in tunnels:
        for c in capsule:
            if c in getATunnel(curPos,tunnels):
                self.capsule = c

    if self.capsule != None:
        features['distanceToCapsule'] = self.getMazeDistance(myPos, self.capsule)
        if myPos == self.capsule:
            features['distanceToCapsule'] = 0
            self.capsule = None

    if len(activeGhost) == 0 and myPos in capsule:
        features['leaveCapsule'] = 0.1

    if action == Directions.STOP: features['stop'] = 1

    if successor.getAgentState(self.index).isPacman and curPos not in tunnels and \
        successor.getAgentState(self.index).getPosition() in tunnels and checkTunnel == 0:
        features['noFoodTunnel'] = -1
 
    if len(activeGhost) > 0:
         dist = min([self.getMazeDistance(curPos, a.getPosition()) for a in activeGhost])
         if checkTunnel != 0 and checkTunnel*2 >= dist-1:
             features['wasteAction'] = -1

    if len(scaredGhost) > 0:
         dist = min([self.getMazeDistance(curPos, a.getPosition()) for a in scaredGhost])
         if checkTunnel != 0 and checkTunnel*2 >= scaredGhost[0].scaredTimer -1:
             features['wasteAction'] = -1

    if curPos in tunnels and len(activeGhost) > 0:
        foodPos = self.getTunnelFood(gameState)
        if foodPos == None:
            features['escapeTunnel'] = self.getMazeDistance(nextPos(curPos,action), self.tunnelEntry)
        else:
            lengthToEscape = self.getMazeDistance(myPos, foodPos) + self.getMazeDistance(foodPos, self.tunnelEntry)
            ghostToEntry = min([self.getMazeDistance(self.tunnelEntry, a.getPosition()) for a in activeGhost])
            if ghostToEntry - lengthToEscape <= 1 and len(scaredGhost) == 0:
                features['escapeTunnel'] = self.getMazeDistance(nextPos(curPos,action), self.tunnelEntry)

    if curPos in tunnels and len(scaredGhost) > 0:
        foodPos = self.getTunnelFood(gameState)
        if foodPos == None:
            features['escapeTunnel'] = self.getMazeDistance(nextPos(curPos,action), self.tunnelEntry)
        else:
            lengthToEscape = self.getMazeDistance(myPos, foodPos) + self.getMazeDistance(foodPos, self.tunnelEntry)
            if  scaredGhost[0].scaredTimer - lengthToEscape <= 1:
                features['escapeTunnel'] = self.getMazeDistance(nextPos(curPos,action), self.tunnelEntry)

    if not gameState.getAgentState(self.index).isPacman and len(activeGhost) > 0 and self.stuckStep != -1:
        self.stuckStep += 1

    if gameState.getAgentState(self.index).isPacman or myPos == self.nextEntrance:
        self.stuckStep = 0
        self.nextEntrance = None

    if self.stuckStep > 10:
        self.stuckStep = -1
        self.nextEntrance = random.choice(self.getEntrance(gameState))   

    if self.nextEntrance != None and features['goToSafeFood'] == 0:
        features['runToNextEntrance'] = self.getMazeDistance(myPos,self.nextEntrance)

    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore':1, 'distToHome':-100, 'safeFoodDist':-2, 'openRoadFood' :-3,'distToGhost': -10, 'die':-1000,'goToSafeFood': -11,'distanceToCapsule': -1200, 
          'return':-1,'leaveCapsule':-1, 'stop':-50, 'noFoodTunnel':100,'wasteAction': 100,'escapeTunnel':-1001,'runToNextEntrance':-1001}


  def getLengthToHome(self, gameState):  
      curPos = gameState.getAgentState(self.index).getPosition()
      width = gameState.data.layout.width
      height = gameState.data.layout.height
      legalPositions = [p for p in gameState.getWalls().asList(False)]
      legalRed = [p for p in legalPositions if p[0] == width / 2 - 1]
      legalBlue = [p for p in legalPositions if p[0] == width / 2]
      if self.red:
          return min([self.getMazeDistance(curPos, a) for a in legalRed])
      else:
          return min([self.getMazeDistance(curPos, a) for a in legalBlue])

  # methods for MCT
  def OfsRollout(self, gameState):
        counter = 2
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghost = [a for a in enemies if not a.isPacman and a.getPosition() is not None]
        ghostPos = [a.getPosition() for a in ghost]
        curState = gameState
        while counter != 0:
            counter -= 1
            actions = curState.getLegalActions(self.index)
            nextAction = random.choice(actions)
            successor = self.getSuccessor(curState, nextAction)
            myPos = nextPos(curState.getAgentState(self.index).getPosition(), nextAction)
            if myPos in ghostPos:
                return -9999
            curState = successor
        return self.evaluate(curState, 'Stop')

  def simulation(self, gameState):
        (x1, y1) = gameState.getAgentPosition(self.index)
        root = Node((gameState, 0, 0))
        mct = Tree(root)
        startTime = time.time()
        while time.time() - startTime < 0.95:
            self.iteration(mct)
        nextState = mct.tree.chooseChild().value[0]
        (x2, y2) = nextState.getAgentPosition(self.index)
        if x1 + 1 == x2:
            return Directions.EAST
        if x1 - 1 == x2:
            return Directions.WEST
        if y1 + 1 == y2:
            return Directions.NORTH
        if y1 - 1 == y2:
            return Directions.SOUTH
        return Directions.STOP

  def iteration(self, mct):
        if mct.tree.children == []:
            self.expand(mct, mct.tree)
        else:
            leaf = mct.select()
            if leaf.value[2] == 0:
                r = self.OfsRollout(leaf.value[0])
                mct.backPropagate(r, leaf)
            elif leaf.value[2] == 1:
                self.expand(mct, leaf)
                newLeaf = random.choice(leaf.children)
                r = self.OfsRollout(newLeaf.value[0])
                mct.backPropagate(r, newLeaf)

  def expand(self, mct, node):
        actions = node.value[0].getLegalActions(self.index)
        actions.remove(Directions.STOP)
        for action in actions:
            successor = node.value[0].generateSuccessor(self.index, action)
            successorNode = Node((successor, 0, 0))
            mct.insert(node, successorNode)


class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getLengthToBoundary(self, gameState):         #Length to the mid map's boundary
      curPos = gameState.getAgentState(self.index).getPosition()
      width = gameState.data.layout.width
      height = gameState.data.layout.height
      legalPositions = [p for p in gameState.getWalls().asList(False)]
      legalRed = [p for p in legalPositions if p[0] == width / 2 - 1]
      legalBlue = [p for p in legalPositions if p[0] == width / 2]
      if self.red:
          return min([self.getMazeDistance(curPos, a) for a in legalRed])
      else:
          return min([self.getMazeDistance(curPos, a) for a in legalBlue])

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    curPos = gameState.getAgentState(self.index).getPosition()
    curState = gameState.getAgentState(self.index)
    sucState = successor.getAgentState(self.index)
    sucPos = sucState.getPosition()
    curCapsule = self.getCapsulesYouAreDefending(gameState)
    lengthToBoundary = self.getLengthToBoundary(successor)
    # Computes whether we're on defense (1) or offense (0)

    features['onDefense'] = 100
    if sucState.isPacman: features['onDefense'] = 0

    if self.runToBoundary == None:
        features['runToBoundary'] = self.getLengthToBoundary(successor)

    if self.getLengthToBoundary(successor) <= 2:
        self.runToBoundary = 0


    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    curEnemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    curInvaders = [a for a in curEnemies if a.isPacman and a.getPosition() != None]

    if self.ifNeedsBlockTunnel(curInvaders, curPos, curCapsule) and curState.scaredTimer == 0:
        features['runToTunnelEntry'] = self.getMazeDistance(getTunnelEntry(curInvaders[0].getPosition(),tunnels,legalPositions),sucPos)
        return features

    if curPos in defensiveTunnels and len(curInvaders) == 0:
        features['leaveTunnel'] = self.getMazeDistance(self.start, sucPos)

    features['numInvaders'] = len(invaders)        
    if len(curInvaders) == 0 and not successor.getAgentState(self.index).isPacman and curState.scaredTimer == 0:
        if  curPos not in defensiveTunnels and successor.getAgentState(self.index).getPosition() in defensiveTunnels: 
            features['wasteAction'] = -1

    if len(invaders) > 0 and curState.scaredTimer == 0:            
        dists = [self.getMazeDistance(sucPos, a.getPosition()) for a in invaders]
        features['invaderDistance'] = min(dists)
        features['lengthToBoundary'] = self.getLengthToBoundary(successor)
    
    if len(invaders) > 0 and curState.scaredTimer != 0:           
        dists = min([self.getMazeDistance(sucPos, a.getPosition()) for a in invaders])
        features['followMode'] = (dists-2)*(dists-2)
        if curPos not in defensiveTunnels and successor.getAgentState(self.index).getPosition() in defensiveTunnels:
            features['wasteAction'] = -1

    if len(invaders) > 0 and len(curCapsule) != 0:         
        dist2 = [self.getMazeDistance(c, sucPos) for c in curCapsule]
        features['protectCapsules'] = min(dist2)


    if action == Directions.STOP: features['stop'] = 1        
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1  

    if self.getPreviousObservation() != None:
      if len(invaders) == 0 and self.ifLostFood() != None:
          self.curLostFood = self.ifLostFood()

      if self.curLostFood != None and len(invaders) == 0: 
          features['goToLostFood'] = self.getMazeDistance(sucPos,self.curLostFood)
      
      if sucPos == self.curLostFood or len(invaders) > 0:
          self.curLostFood = None

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -100, 'onDefense': 10, 'invaderDistance': -10, 'stop': -100, 'reverse': -2,'lengthToBoundary':-3,
     'protectCapsules': -3, 'wasteAction':200,'followMode':-100, 'runToTunnelEntry': -10, 'leaveTunnel':-0.1,'runToBoundary':-2,'goToLostFood':-1}

  
  def ifNeedsBlockTunnel(self, curInvaders, currentPostion, curCapsule): 
    if len(curInvaders) == 1:
      invadersPos = curInvaders[0].getPosition()
      if invadersPos in tunnels:
        tunnelEntry = getTunnelEntry(invadersPos, tunnels, legalPositions)
        if self.getMazeDistance(tunnelEntry,currentPostion) <= self.getMazeDistance(tunnelEntry,invadersPos) and curCapsule not in getATunnel(invadersPos,tunnels):
           return True
    return False

  def ifLostFood(self):
        preState = self.getPreviousObservation()
        currState = self.getCurrentObservation()
        myCurrFood = self.getFoodYouAreDefending(currState).asList()
        myLastFood = self.getFoodYouAreDefending(preState).asList()
        if len(myCurrFood) < len(myLastFood):
            for i in myLastFood:
                if i not in myCurrFood:
                    return i
        return None

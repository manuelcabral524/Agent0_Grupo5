import client
import ast
import random

VISITED_COLOR = "#400000" # Vermelho escuro.
FRONTIER_COLOR = "red3" # Vermelho claro.

# AUXILIAR

class Stack:
    def __init__(self):
         self.stack_data = []

    def isEmpty(self):
        if len(self.stack_data) == 0:
            return True
        else:
            return False

    def pop(self):
        return self.stack_data.pop(len(self.stack_data) - 1)

    def insert(self, element):
        return self.stack_data.append(element)

    def getStack(self):
        return self.stack_data

    def getLength(self):
        return len(self.stack_data)

    def __iter__(self):
        ''' Returns the Iterator object '''
        return StackIterator(self)

    def getValueAtIndex(self, i):
        return self.stack_data[i]

class StackIterator:
   ''' Iterator class '''
   def __init__(self, stack):
       # Stack object reference
       self._stack = stack
       # member variable to keep track of current index
       self._index = self._stack.getLength() - 1
   def __next__(self):
       ''''Returns the next value from stack object's lists '''
       if self._index >= 0:
           result = (self._stack.getStack()[self._index])
           self._index -= 1
           return result
       # End of Iteration
       raise StopIteration

class Queue:
    def __init__(self):
         self.queue_data = []

    def isEmpty(self):
        if len(self.queue_data) == 0:
            return True
        else:
            return False

    def pop(self):
        return self.queue_data.pop(0)

    def insert(self,element):
        return self.queue_data.append(element)

    def getQueue(self):
        return self.queue_data

    def __iter__(self):
        ''' Returns the Iterator object '''
        return QueueIterator(self)

class QueueIterator:
   ''' Iterator class '''
   def __init__(self, queue):
       # Queue object reference
       self._queue = queue
       # member variable to keep track of current index
       self._index = 0
   def __next__(self):
       ''''Returns the next value from queue object's lists '''
       if self._index < len(self._queue.getQueue()):
           result = (self._queue.getQueue()[self._index])
           self._index +=1
           return result
       # End of Iteration
       raise StopIteration

# SEARCH AGENT

class Node:
    def __init__(self,state,parent,action,path_cost,level):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.level = level

    def getState(self):
        return self.state

    def getParent(self):
        return self.parent

    def getAction(self):
        return self.action

    def getPathCost(self):
        return self.path_cost

    def getLevel(self):
        return self.level

class Agent:
    def __init__(self):
        self.c = client.Client('127.0.0.1', 50001)
        self.res = self.c.connect()
        random.seed()  # To become true random, a different seed is used! (clock time)
        self.visited_nodes = Stack()
        self.frontier_nodes = Stack()
        self.weightMap =[]
        self.goalNodePos =(0,0)
        self.state = (0,0)
        self.maxCoord = (0,0)

    def getConnection(self):
        return self.res

    def getGoalPosition(self):
        msg = self.c.execute("info", "goal")
        goal = ast.literal_eval(msg)
        # test
        print('Goal is located at:', goal)
        return goal

    def getSelfPosition(self):
        msg = self.c.execute("info", "position")
        pos = ast.literal_eval(msg)
        # test
        print('Received agent\'s position:', pos)
        return pos

    def getWeightMap(self):
        msg = self.c.execute("info", "map")
        w_map = ast.literal_eval(msg)
        # test
        print('Received map of weights:', w_map)
        return w_map

    def getPatchCost(self,pos):
        return self.weightMap[pos[0]][pos[1]]

    def getMaxCoord(self):
        msg = self.c.execute("info","maxcoord")
        max_coord =ast.literal_eval(msg)
        # test
        print('Received maxcoord', max_coord)
        return max_coord

    def getObstacles(self):
        msg = self.c.execute("info","obstacles")
        obst =ast.literal_eval(msg)
        # test
        print('Received map of obstacles:', obst)
        return obst

    # COM MODIFICAÇÕES NO SERVIDOR
    def getObjectsAt(self, x, y):
        msg = self.c.execute("info", str(x)+","+str(y))
        return ast.literal_eval(msg)

    # COM MODIFICAÇÕES NO SERVIDOR
    def isVisitable(self, x, y):
        return all(obj != "obstacle" and obj != "bomb" for obj in self.getObjectsAt(x,y))

    def step(self,pos,action):
        if action == "east":
            if pos[0] + 1 < self.maxCoord[0]:
                new_pos = (pos[0] + 1, pos[1])
            else:
                new_pos =(0,pos[1])

        if action == "west":
            if pos[0] - 1 >= 0:
                new_pos = (pos[0] - 1, pos[1])
            else:
                new_pos = (self.maxCoord[0] - 1, pos[1])

        if action == "south":
            if pos[1] + 1 < self.maxCoord[1]:
                new_pos = (pos[0], pos[1] + 1 )
            else:
                new_pos = (pos[0], 0)

        if action == "north":
            if pos[1] - 1 >= 0:
                new_pos = (pos[0], pos[1] - 1)
            else:
                new_pos = (pos[0], self.maxCoord[1] - 1 )
        return new_pos


    def getNode(self,parent_node,action,level):
        state = self.step(parent_node.getState(),action)
        pathCost = parent_node.getPathCost() + self.getPatchCost(state)
        return Node(state, parent_node, action, pathCost,level)

    def printNodes(self,type,nodes,i):
        print(type," (round ",i," )")
        print("state | path cost")
        for node in nodes:
            print(node.getState(),"|", node.getPathCost())

    def printPath(self, node):
        n = node
        n_list = []
        while n.getPathCost() != 0:
            n_list.insert(0,[n.getState(), n.getPathCost()])
            n = n.getParent()
        print("Final Path", n_list)

    def mark_visited(self, node):
        # self.c.execute("mark_visited", str(node.getState())[1:-1].replace(" ", ""))
        self.c.execute("mark", str(node.getState())[1:-1].replace(" ", "") + "_" + VISITED_COLOR)

    def mark_frontier(self, node):
        # self.c.execute("mark_frontier", str(node.getState())[1:-1].replace(" ", ""))
        self.c.execute("mark", str(node.getState())[1:-1].replace(" ", "") + "_" + FRONTIER_COLOR)

    def think(self):
        # Get the position of the Goal
        self.goalNodePos = self.getGoalPosition()
        # Get information of the weights for each step in the world ...
        self.weightMap = self.getWeightMap()
        # Get max coordinates
        self.maxCoord = self.getMaxCoord()
        # Get the initial position of the agent
        self.state = self.getSelfPosition()

        root = Node(self.state, None, "", 0, 0)
        end = False
        i = 0
        # lista_visitados=[]
        # nos_fronteira_atual = []

        # Lista de obstáculos.
        obstaculos = []
        # Adicionar obstáculos à lista.
        for column in range(len(self.getObstacles())):
            for row in range(len(self.getObstacles()[column])):
                if (self.getObstacles()[column][row] == 1):
                    obstaculos.append((column, row))

        # O ciclo while começa com o nó inicial, root.
        v = root
        # nivel: profundidade atual.
        nivel = 0
        # limite: profundidade limite.
        limite = 2000
        # Pesquisa em Profundidade.
        while (end == False):
            # Incremento da profundidade atual.
            nivel = nivel + 1
            if (nivel > limite):
                input("Não foi possível atingir o objetivo com esse limite de profundidade.")
                end = True
            else:
                if (self.state == self.goalNodePos):
                    # Visitar o nó.
                    self.visited_nodes.insert(v)
                    # Marcar a vermelho escuro o nó visitado.
                    self.mark_visited(v)
                    end = True
                else:
                    # Visitar o nó.
                    self.visited_nodes.insert(v)
                    # Marcar a vermelho escuro o nó visitado.
                    self.mark_visited(v)

                    for d in ["north", "east", "south", "west"]:
                        no_fronteira = self.getNode(v, d, nivel)
                        # Regista os nós fronteira se não forem obstáculos, se não foram visitados
                        # e se não estão no Stack dos nós fronteira.
                        if no_fronteira.getState() not in obstaculos:
                            if no_fronteira.getState() not in [n.getState() for n in self.visited_nodes.getStack()]:
                                if no_fronteira.getState() not in [f.getState() for f in self.frontier_nodes.getStack()]:
                                    self.frontier_nodes.insert(no_fronteira)
                                    # Marca a vermelho claro os nós fronteira.
                                    self.mark_frontier(no_fronteira)

                    self.printNodes("Frontier", self.frontier_nodes, i)
                    print("-------------------------------------------")
                    self.printNodes("Visited", self.visited_nodes, i)
                    print("-------------------------------------------")

                    # Lista para guardar valores que são retirados do Stack (self.frontier.nodes)
                    # para depois serem inseridos de volta.
                    stack_values = []
                    # Percorrer nós fronteira.
                    for w in range(3):
                        w = self.frontier_nodes.pop()
                        # Se a profundidade atual for menor que a profundidade limite
                        # e se o nó ainda não foi visitado, visita-se o nó e retira-se do stack
                        # dos nós fronteira.
                        if w.level <= limite:
                            v = w
                            self.state = v.getState()
                            i += 1
                            for index in range(len(stack_values)-1, -1, -1):
                                self.frontier_nodes.insert(stack_values[index])
                            break
                        else:
                            stack_values += w
                            continue
        self.do(v)
        input("GOAL FOUND! CONGRATULATIONS")

    def turn_and_go(self, direction):
        if direction == "south":
            left, right, back = "east", "west", "north"
        elif direction == "north":
            left, right, back = "west", "east", "south"
        elif direction == "east":
            left, right, back = "north", "south", "west"
        elif direction == "west":
            left, right, back = "south", "north", "east"
        if self.getSelfDirection() == back:
            self.c.execute("command", "right")
            self.c.execute("command", "right")
        elif self.getSelfDirection() == right:
            self.c.execute("command", "left")
        elif self.getSelfDirection() == left:
            self.c.execute("command", "right")
        self.c.execute("command", "forward")

    def do(self, path):
        self.c.execute("command", "set_steps")
        for node in path:
            coords = node[0]
            position = self.getSelfPosition()
            dx, dy = coords[0]-position[0], coords[1]-position[1]

            if abs(dx) != 1:
                dx = -dx
            if abs(dy) != 1:
                dy = -dy

            if dy > 0:
                self.turn_and_go("south")  # , "east", "west", "north")
            elif dy < 0:
                self.turn_and_go("north")  # , "west", "east", "south")
            elif dx > 0:
                self.turn_and_go("east")  # , "north", "south", "west")
            else:
                self.turn_and_go("west")  # , "south", "north", "east")
        input("Waiting for return")

    def getSelfDirection(self):
        return self.c.execute("info", "direction")


#STARTING THE PROGRAM:
def main():
    print("Starting client!")
    ag = Agent()
    if ag.getConnection() != -1:
        path = ag.think()
        if path is not None:
            ag.do(path)
        else:
            print("Goal not found!")

main()
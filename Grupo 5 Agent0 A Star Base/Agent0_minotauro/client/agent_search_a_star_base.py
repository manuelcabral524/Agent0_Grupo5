import client
import ast
import random
import math

VISITED_COLOR = "#400000" # Vermelho escuro.
FRONTIER_COLOR = "red3" # Vermelho claro.

# AUXILIAR

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


# Node
class Node:
    def __init__(self, state, parent, action, path_cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.fCost = 0
        self.hCost = 0

    def getState(self):
        return self.state

    def getParent(self):
        return self.parent

    def getAction(self):
        return self.action

    def getPathCost(self):
        return self.path_cost

    def getFCost(self):
        return self.fCost

    def getHCost(self):
        return self.hCost


# SEARCH AGENT
class Agent:
    def __init__(self):
        self.c = client.Client('127.0.0.1', 50001)
        self.res = self.c.connect()
        random.seed()  # To become true random, a different seed is used! (clock time)
        self.visited_nodes = Queue()
        self.frontier_nodes = Queue()
        self.nos_possiveis_expandir = Queue()
        self.weightMap = []
        self.goalNodePos =(0,0)
        self.state = (0,0)
        self.maxCoord = (0,0)
        self.obstaculos = []

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
        obst = ast.literal_eval(msg)
        # test
        #print('Received map of obstacles:', obst)
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


    def getNode(self,parent_node,action):
        state = self.step(parent_node.getState(),action)
        pathCost = parent_node.getPathCost() + self.getPatchCost(state)
        return Node(state, parent_node, action, pathCost)

    def printNodes(self,type,nodes,i):
        print(type," (round ",i," )")
        print("state | path cost | F cost | G cost | H cost")
        for node in nodes:
            print(node.getState(),"|", node.getPathCost(), "|", node.getFCost(), "=", node.getFCost()-node.getHCost(), "+", node.getHCost())

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

    # Obter nós fronteira.
    def getNosFronteira(self, v, gCost):
        for d in ["north", "east", "south", "west"]:
            no_fronteira = self.getNode(v, d)
            coord_no_fronteira = no_fronteira.getState()
            # Regista os nós fronteira se não forem obstáculos, se não foram visitados
            # e se não estão na Queue dos nós fronteira.
            if self.getObstacles()[coord_no_fronteira[0]][coord_no_fronteira[1]] != 1:
                if coord_no_fronteira not in [n.getState() for n in self.visited_nodes]:
                    no_fronteira.fCost = self.f(gCost + no_fronteira.getPathCost(), no_fronteira)
                    self.frontier_nodes.insert(no_fronteira)
                    # Marca a vermelho claro os nós fronteira.
                    self.mark_frontier(no_fronteira)

    """
    Função h(n).
    Calcula a heurística, ou seja, o custo estimado desde um dado nó ao nó objetivo.
    A fórmula utilizada é a distância de Manhattan. 
    Parâmetros:
        n -> um nó.
    Return:
        h(n) = |Xstart - Xdestination| + |Ystart - Ydestination|
    """
    def h(self, n):
        nState = n.getState()
        gState = self.getGoalPosition()
        nX = nState[0]
        nY = nState[1]
        gX = gState[0]
        gY = gState[1]

        n.hCost = math.fabs(nX-gX) + math.fabs(nY-gY)

        return n.hCost

    # Função F(n) = G(n) + H(n)
    def f(self, gCost, node):
        return gCost + self.h(node)

    def think(self):
        # Get the position of the Goal
        self.goalNodePos = self.getGoalPosition()
        # Get information of the weights for each step in the world ...
        self.weightMap = self.getWeightMap()
        # Get max coordinates
        self.maxCoord = self.getMaxCoord()
        # Get the initial position of the agent
        self.state = self.getSelfPosition()

        # Adicionar primeiro nó.
        root = Node(self.state, None, "", 0)

        # O ciclo while começa com o nó inicial, root.
        v = root

        # Lista com os todos os nós conhecidos.
        # Têm prioridade os nós conhecidos mais recentes e por ordem de menor F cost.
        # Funciona como uma Priority Queue.
        nos_conhecidos = []

        end = False
        i = 0
        gCost = 0

        # Algoritmo A* (etapa base).
        while end != True:
            i += 1
            # Visitar o nó.
            self.visited_nodes.insert(v)
            # Marcar a vermelho escuro o nó visitado.
            self.mark_visited(v)
            print("G cost atual:", gCost)
            if v.getState() == self.goalNodePos:
                print("Vitória!")
                print("-------------------------------------------")
                self.printNodes("Visited", self.visited_nodes, i)
                end = True
            else:
                # Buscar nós fronteira do nó atual.
                self.getNosFronteira(v, gCost)

                no_custo_menor = self.frontier_nodes.getQueue()[0]
                # Lista auxiliar com os atuais nós fronteira ordenados por ordem crescente de F cost.
                aux = [no_custo_menor]
                # Ordenar por ordem crescente de F cost, na lista 'aux'.
                for w in self.frontier_nodes:
                    # Se for o menor vai para o inicio da lista.
                    if w.getFCost() < aux[0].getFCost():
                        print("ola2")
                        aux.insert(0, w)
                    # Se for o maior vai para o fim da lista.
                    elif w.getFCost() > aux[len(aux)-1].getFCost():
                        print("ola3")
                        aux.append(w)
                    # Se estiver entre o menor e o maior valor da lista...
                    # Percorrer a lista e encontrar o lugar.
                    elif aux[0].getFCost() < w.getFCost() < aux[len(aux) - 1].getFCost():
                        print("ola4")
                        for x in range(len(aux)):
                            if aux[x].getFCost() < w.getFCost() < aux[x+1].getFCost():
                                print("ola5")
                                aux.insert(x+1, w)
                    # Se tiverem o mesmo F cost, fica primeiro o que tem menor H cost.
                    else:
                        for y in range(len(aux)):
                            print("ola6")
                            if w.getFCost() == aux[y].getFCost() and w.getState() != aux[y].getState():
                                print("ola7")
                                if w.getHCost() < aux[y].getHCost():
                                    print("ola8")
                                    aux.insert(y, w)
                                else:
                                    print("ola9")
                                    aux.insert(y+1, w)
                                break

                # Atualizar lista de nós conhecidos.
                for a in range(len(aux)-1, -1, -1):
                    nos_conhecidos.insert(0, aux[a])

                # O próximo nó a visitar é o nó com menor F cost.
                v = nos_conhecidos[0]

                # Atualizar G cost.
                gCost += v.path_cost

                # Prints
                print("-------------------------------------------")
                self.printNodes("Frontier", self.frontier_nodes, i)
                print("-------------------------------------------")
                self.printNodes("Visited", self.visited_nodes, i)
                print("-------------------------------------------")
                print("Nós conhecidos: (round", i, ")")
                for n in nos_conhecidos:
                    print(n.getState(), "F(n)=", n.getFCost(), "(", n.getFCost()-n.getHCost(), "+", n.getHCost(), ")")
                print("-------------------------------------------")

                # Limpar Queue dos nós fronteira para a proxima iteração.
                self.frontier_nodes = Queue()

        path = []
        for node in self.visited_nodes:
            path.append(node)

        return path

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

        for i in range(len(path) - 1):
            node = path[i]
            next_node = path[i+1]
            coords = node.getState()
            next_coords = next_node.getState()
            position = self.getSelfPosition()

            x = coords[0]
            y = coords[1]

            next_x = next_coords[0]
            next_y = next_coords[1]

            if next_x > x and next_y > y:
                self.turn_and_go("east")
            elif next_x < x and next_y == y:
                self.turn_and_go("west")
            elif next_x == x and next_y > y:
                self.turn_and_go("south")
            else:
                self.turn_and_go("north")
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

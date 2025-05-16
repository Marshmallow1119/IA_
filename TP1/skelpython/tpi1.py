#STUDENT NAME: Tomás Rafael Marques Brás
#STUDENT NUMBER: 112665

#DISCUSSED TPI-1 WITH: (names and numbers):


from tree_search import *
from strips import *
from blocksworld import *

class MyNode(SearchNode):

    def __init__(self,state,parent,depth=0,cost=0,heuristic=0,action=None):
        super().__init__(state,parent)
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.action = action
        self.parent = parent

    def in_parent(self,state):
        if self.parent == None:
            return False
        if self.parent.state == state:
            return True
        return self.parent.in_parent(state)


class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth',improve=False):
        super().__init__(problem,strategy)
        root = MyNode(problem.initial, None, 0, 0, 0, None)
        self.open_nodes = [root]
        self.strategy= strategy
        self.problem = problem
        self.num_open=1
        self.num_closed=0
        self.num_solution=0
        self.num_skipped=0
        self.improve=improve
        self.terminals=1
        self.non_terminals=0
        self.sum_depths=0
        self.plan=[]

    def astar_add_to_open(self,lnewnodes):
        self.open_nodes.extend(lnewnodes)
        self.open_nodes.sort(key=lambda x: (x.cost + x.heuristic,x.depth,str(x.state)))

    def informeddepth_add_to_open(self,lnewnodes):
        lnewnodes.sort(key=lambda x: (x.cost + x.heuristic, str(x.state)))
        self.open_nodes[:0] = lnewnodes
    
    def search2(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            self.num_open -= 1
            if self.problem.goal_test(node.state):
                self.num_solution += 1
                if self.solution == None or node.cost < self.solution.cost:
                    self.solution = node
                    self.plan = self.get_plan(node)
                if not self.improve:
                    return self.get_path(self.solution)
            elif self.solution != None and (node.cost + node.heuristic) >= self.solution.cost:
                self.num_skipped += 1
                continue
            else:
                self.num_closed += 1            
                lnewnodes = []
                self.non_terminals +=1  
                for action in self.problem.domain.actions(node.state):
                    newstate = self.problem.domain.result(node.state,action) #cidade destino
                    if  not node.in_parent(newstate):
                        cost=self.problem.domain.cost(node.state,action)
                        heuristic=self.problem.domain.heuristic(newstate,self.problem.goal)

                        if newstate not in self.get_path(node):
                            newnode = MyNode(newstate,node,node.depth+1,node.cost + cost,heuristic,action) #custo do pai mais o da ação
                            lnewnodes.append(newnode)

                        self.sum_depths += newnode.depth

                self.num_open += len(lnewnodes)
                self.add_to_open(lnewnodes)
                self.terminals = len(self.open_nodes) 

        return self.get_path(self.solution) 
        
    def check_admissible(self, node):
        total_cost = node.cost
        current_node = node
        
        while current_node is not None:
            if current_node.heuristic > total_cost - current_node.cost:
                return False
            current_node = current_node.parent
        return True

    def get_plan(self,node):
        plan = []
        while node is not None:
            if node.action is not None:
                plan.insert(0,node.action)
            node = node.parent
        return plan


class MyBlocksWorld(STRIPS):
    def heuristic(self, state, goal):
        """
        Calcula uma heurística baseada em penalidades de blocos fora do lugar e
        em movimentos necessários para empilhar adequadamente os elementos.
        """
        heuristic_cost = 0
        state_dict = self.create_state_dict(state)

        goal_on = {pred.args[0]: pred.args[1] for pred in goal if len(pred.args) == 2}

        penalty_weights = {
            "On": 1.25,
            "Free": 0.1,
            "Floor": 1,
            "Holds": 0.1
        }

        for goal_predicate in goal:
            if goal_predicate in state:
                continue  

            if len(goal_predicate.args) == 2:
                block1, block2 = goal_predicate.args
                if block1 not in state_dict.get("On", {}).get(block2, []):
                    penalty = penalty_weights["On"] + self.distance_penalty(block1, block2, state_dict)
                    heuristic_cost += penalty

            elif len(goal_predicate.args) == 1:
                block = goal_predicate.args[0]
                if "Free" in str(goal_predicate) and block not in state_dict["Free"]:
                    heuristic_cost += penalty_weights["Free"]
                elif "Floor" in str(goal_predicate) and block not in state_dict["Floor"]:
                    heuristic_cost += penalty_weights["Floor"]
                elif "Holds" in str(goal_predicate) and block not in state_dict["Holds"]:
                    heuristic_cost += penalty_weights["Holds"]

        heuristic_cost += max(heuristic_cost, self.h2(state_dict["On"], goal_on), self.h1(state_dict["On"], goal_on)) - 2.5
        return int(heuristic_cost)


    def h1(self, state_on, goal_on):
        """
        Calcula a heurística verificando a ordem dos blocos em cada pilha de destino.
        Caso um bloco esteja incorreto, todos acima dele são considerados fora do lugar.
        """
        heuristic_cost = 0
        for goal_block, goal_target in goal_on.items():
            current_block = goal_block
            while current_block is not None:
                if current_block not in state_on or state_on[current_block] != goal_target:
                    heuristic_cost += 1
                    current_block = state_on.get(current_block)
                else:
                    break
        return heuristic_cost

    def h2(self, state_on, goal_on):
        """
        Verifica a quantidade de movimentos extras necessários para reempilhar blocos que estão fora da posição.
        """
        extra_moves = 0
        processed_blocks = set()

        for block, target in state_on.items():
            if block in processed_blocks:
                continue

            if block in goal_on and goal_on[block] is None:
                if target is not None:
                    extra_moves += 1
                processed_blocks.add(block)

            elif block in goal_on and goal_on[block] != target:
                extra_moves += 1
                processed_blocks.add(block)

            elif block not in goal_on:
                current_block = block
                temp_processed = set()
                requires_unstacking = False

                while current_block in state_on:
                    if current_block in goal_on and goal_on[current_block] != state_on.get(current_block):
                        requires_unstacking = True
                        break
                    temp_processed.add(current_block)
                    current_block = state_on[current_block]

                if requires_unstacking:
                    extra_moves += len(temp_processed) - 1 
                else:
                    extra_moves += len(temp_processed)

                processed_blocks.update(temp_processed)

        return extra_moves

    def distance_penalty(self, block1, block2, state_dict):
        """
        Penalidade de distância que diminui com o aumento de blocos intermediários,
        ajudando a manter a admissibilidade e reduzindo a expansão excessiva.
        """
        penalty = 0
        current_block = block1
        distance_increment = 0  # Penalidade inicial
        
        while current_block in state_dict.get("On", {}) and state_dict["On"][current_block]:
            next_block = next(iter(state_dict["On"][current_block]))
            penalty += distance_increment
            distance_increment *= 0.4  # Redução progressiva da penalidade
            current_block = next_block
            if current_block == block2:
                break
                
        return penalty

    def create_state_dict(self, state):
        """
        Converte o estado para um dicionário de estruturas, facilitando a verificação de onde cada bloco está.
        """
        state_dict = {"On": {}, "Free": set(), "Floor": set(), "Holds": set()}

        for predicate in state:
            if not predicate.args:
                continue
            
            if len(predicate.args) == 2:
                block1, block2 = predicate.args
                state_dict["On"][block1] = block2  # Mapeamento direto: bloco -> bloco abaixo
            elif "Free" in str(predicate):
                state_dict["Free"].add(predicate.args[0])
            elif "Floor" in str(predicate):
                state_dict["Floor"].add(predicate.args[0])
            elif "Holds" in str(predicate):
                state_dict["Holds"].add(predicate.args[0])

        return state_dict

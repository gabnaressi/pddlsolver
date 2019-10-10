# fix pddlpy with https://stackoverflow.com/questions/46079258/cant-import-module-antlr-mygrammarlexer-and-mygrammarparser
from collections import Counter
from copy import deepcopy, copy
import pddlpy
from queue import PriorityQueue
from datetime import datetime
from math import inf
import pdb
import cProfile


def hash_state(state):
        return hash(tuple(state.predicates))
        
def is_applicable(state, action):
    # input: state of class State, action of class Operator
    if(action.precondition_pos.issubset(state.predicates)):
        return True
    else:
        return False
    
def apply_action(state, action, isHeuristic=False):
    #if(is_applicable(state,action)):
    state_ret = state.copy()
    
    state_ret.add_predicates(action.effect_pos)
    if(not isHeuristic):
        state_ret.remove_predicates(action.effect_neg)
    state_ret.register_action(action)
    state_ret.hash_state()
    return state_ret        
        
class State:
    def __init__(self):
        self.predicates = set()
        self.h = inf;
        self.g = 0;
        self.hash = None;
        self.action_path = [];
    
    def add_predicate(self,predicate):
        self.predicates.add(predicate)
        
    def add_predicates(self,predicate_set):
        self.predicates.update(predicate_set)
        
    def remove_predicates(self, predicate_set):
        self.predicates.difference_update(predicate_set)        

    def hash_state(self):
        self.hash = hash(tuple(self.predicates))
        return self.hash
        
    def register_action(self, action):
        self.action_path.append(action)
        self.g = self.g + 1

    def calculate_heuristic(self,method):
        if(method=='1'):
            self.h = 1
        elif(method=='FF'):
            self.h = heuristica_FF(self)
           
    
    def cost(self):
        return self.g + self.h
    
    def __lt__(self, other):
        return self.cost() < other.cost()
    
    def __str__(self):
        return(str(self.cost()))
    
    def __repr__(self):
        return(str(self.cost()))
    
    def copy(self):
        ret = State()
        ret.add_predicates(self.predicates)
        ret.action_path = list(self.action_path)
        return ret
    
# Le o PDDL
problema = pddlpy.DomainProblem('C:/Users/Gabriel/Desktop/ep_plan/robot_domain.pddl','C:/Users/Gabriel/Desktop/ep_plan/robot_problem.pddl')
  
estado_objetivo = State()
for atom in problema.goals():
    estado_objetivo.add_predicate(tuple(atom.predicate))
hash_objetivo = estado_objetivo.hash_state()
  
def heuristica_FF(state): 
    camadas = [state]
    
    while (not (camadas[-1].predicates.issuperset(estado_objetivo.predicates)) ):
        proxEstado = (camadas[-1]).copy()
        for operator in list(problema.operators()):
                problema_copia = deepcopy(problema)
                for action in list(problema_copia.ground_operator(operator)):
                    if(is_applicable(camadas[-1],action)):
                        proxEstado.add_predicates(apply_action(proxEstado, action, True).predicates)
        if(camadas[-1].predicates == proxEstado.predicates):
            return inf
        camadas.append(proxEstado)    
    return len(camadas)

HEURISTICA = '1'



# Cria o estado inicial
estado_inicial = State()
for atom in problema.initialstate():
    estado_inicial.add_predicate(tuple(atom.predicate))
estado_inicial.calculate_heuristic(HEURISTICA)




# https://ae4.tidia-ae.usp.br/access/content/group/a13a6c45-779e-45bf-a740-e1bfe059b8b6/Parte%20I/Aula6-GraphplanParteII.pdf
# https://ae4.tidia-ae.usp.br/access/content/group/a13a6c45-779e-45bf-a740-e1bfe059b8b6/EP1-2019-Karina.pdf

# A*
def a_estrela(problem, heuristic):
    tempo_inicio= datetime.now()
    fila_prioridade = PriorityQueue()
    fila_prioridade.put(estado_inicial)
    estados_conhecidos = [hash_state(estado_inicial)]
    estados_visitados = 0 
    estados_gerados = 0
    ramificacoes = []
    
    while(not fila_prioridade.empty()):
        estados_visitados = estados_visitados + 1
        atual = fila_prioridade.get()        
        ramificacao_atual = 0
        
        # Condicao de parada
        if(atual.predicates.issuperset(estado_objetivo.predicates)):
            print('PLANO:')
            print(*[ str(x.operator_name) +':'+ str(x.variable_list) for x in atual.action_path], sep='\n')
            print('TAMANHO DO PLANO:')
            print(atual.cost())
            print('NUMERO DE ESTADOS VISITADOS:')
            print(estados_visitados)
            print('NUMERO DE ESTADOS GERADOS:')
            print(estados_gerados)
            print('FATOR DE RAMIFICACAO:')
            print(sum(ramificacoes) / len(ramificacoes))
            #return atual.action_path;
            print('TEMPO DE EXECUÇÃO:' + str((datetime.now() - tempo_inicio).seconds) + ' SEGUNDOS')
            break
        
        # Expansao de nos
        for operator in list(problema.operators()):
            problema_copia = deepcopy(problema)
            for action in list(problema_copia.ground_operator(operator)):
                if(is_applicable(atual,action)):
                    result_state = apply_action(atual, action, False)
                    estados_gerados = estados_gerados + 1
                    if(hash_state(result_state) not in estados_conhecidos):
                        ramificacao_atual = ramificacao_atual + 1
                        result_state.calculate_heuristic(HEURISTICA)
                        result_state.cost()
                        fila_prioridade.put(result_state)
                        estados_conhecidos.append(hash_state(result_state))
        
        ramificacoes.append(ramificacao_atual)
    return False
    
a_estrela(problema, 'none')
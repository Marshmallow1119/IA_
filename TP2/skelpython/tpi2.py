#encoding: utf8
# YOUR NAME: Tomás Rafael Marques Brás
# YOUR NUMBER: 112665
from semantic_network import *
from constraintsearch import *
from bayes_net import *
from itertools import product

class MySN(SemanticNetwork):
    def __init__(self):SemanticNetwork.__init__(self)
    def query(self, entity, relname):
        rel_types = {}
        for decl in self.query_local(e1=None, relname=relname):
            rel_type = type(decl.relation)
            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
        if not rel_types:return []  
        rel_type = max(rel_types, key=rel_types.get)
        entities_to_check = [entity]
        checked_entities = set()
        while entities_to_check:
            current_entity = entities_to_check.pop(0)
            if current_entity in checked_entities:
                continue
            checked_entities.add(current_entity)
            supertypes = [decl.relation.entity2 for decl in self.declarations if isinstance(decl.relation, Subtype) and decl.relation.entity1 == current_entity]
            entities_to_check.extend(supertypes)
            member_types = [decl.relation.entity2 for decl in self.declarations if isinstance(decl.relation, Member) and decl.relation.entity1 == current_entity]
            entities_to_check.extend(member_types)
        if rel_type in [Member, Subtype]:
            return [decl.relation.entity2 for decl in self.declarations if decl.relation.name == relname and decl.relation.entity1 == entity]
        elif rel_type == AssocOne:
            values = [decl.relation.entity2 for decl in self.declarations if decl.relation.name == relname and decl.relation.entity1 in checked_entities and isinstance(decl.relation, AssocOne)]
            return [max(set(values), key=values.count)] if values else []
        elif rel_type == AssocNum:
            direct_values = [decl.relation.entity2 for decl in self.declarations if decl.relation.name == relname and decl.relation.entity1 == entity and isinstance(decl.relation, AssocNum)]
            if direct_values:
                return [(sum(direct_values) / len(direct_values))]
            inherited_values = [decl.relation.entity2 for decl in self.declarations if decl.relation.name == relname and decl.relation.entity1 in checked_entities and isinstance(decl.relation, AssocNum)]
            return [(sum(inherited_values) / len(inherited_values))] if inherited_values else []
        elif rel_type == AssocSome:
            values = set(decl.relation.entity2 for decl in self.declarations if decl.relation.name == relname and decl.relation.entity1 in checked_entities and isinstance(decl.relation, AssocSome))
            return list(values)
        return []

class MyBN(BayesNet):
    def __init__(self):BayesNet.__init__(self)
    def test_independence(self, v1, v2, given):
        graph = self._build_graph(v1, v2, given)
        independence = self._is_independent(graph, v1, v2)
        return graph, independence
    def _build_graph(self, v1, v2, given):
        graph = set() 
        variables = set([v1, v2]) | set(given)
        ancestors = self._find_ancestors(variables)
        for var in ancestors:
            for parents in self.dependencies[var]:
                for parent in parents[0]:
                    graph.add((var, parent) if var < parent else (parent, var))
        for var in ancestors:
            parents = set()
            for parent_set, _, _ in self.dependencies[var]:
                parents.update(parent_set)
            parent_list = list(parents)
            for i in range(len(parent_list)):
                for j in range(i + 1, len(parent_list)):
                    graph.add((parent_list[i], parent_list[j]))
        graph = {(u, v) for u, v in graph if u not in given and v not in given}
        return list(graph)
    def _find_ancestors(self, variables):
        ancestors = set(variables)
        queue = list(variables)
        while queue:
            var = queue.pop(0)
            for parent_set, _, _ in self.dependencies[var]:
                for parent in parent_set:
                    if parent not in ancestors:
                        ancestors.add(parent)
                        queue.append(parent)
        return ancestors
    def _is_independent(self, graph, v1, v2):
        visited = set()
        return not self._dfs(graph, v1, v2, visited)
    def _dfs(self, graph, start, end, visited):
        if start == end:
            return True
        visited.add(start)
        for neighbor in [v for u, v in graph if u == start] + [u for u, v in graph if v == start]:
            if neighbor not in visited:
                if self._dfs(graph, neighbor, end, visited):
                    return True
        return False
    
class MyCS(ConstraintSearch):
    def __init__(self,domains,constraints):ConstraintSearch.__init__(self,domains,constraints)
    def search_all(self, domains=None):
        if domains is None:
            domains = self.domains
        self.calls += 1
        if any(len(values) == 0 for values in domains.values()):
            return []
        if all(len(values) == 1 for values in domains.values()):
            return [{var: values[0] for var, values in domains.items()}]
        variable = min((var for var in domains if len(domains[var]) > 1), key=lambda v: len(domains[v]))
        solutions = []
        for value in domains[variable]:
            new_domains = {var: list(vals) for var, vals in domains.items()}
            new_domains[variable] = [value]
            self.propagate(new_domains, variable)
            solutions.extend(self.search_all(new_domains))
        unique_solutions = []
        seen = set()
        for solution in solutions:
            frozen_solution = frozenset(solution.items())
            if frozen_solution not in seen:
                seen.add(frozen_solution)
                unique_solutions.append(solution)
        return unique_solutions
    
def handle_ho_constraint(domains, constraints, variables, constraint):
    aux_var = ''.join(variables) 
    domains[aux_var] = [tuple(values) for values in product(*(domains[var] for var in variables)) if constraint(values)]
    for i, var in enumerate(variables):
        constraints[(aux_var, var)] = lambda aux, aux_val, var, var_val, idx=i: aux_val[idx] == var_val
        constraints[(var, aux_var)] = lambda var, var_val, aux, aux_val, idx=i: aux_val[idx] == var_val
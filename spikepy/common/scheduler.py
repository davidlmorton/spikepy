"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from collections import defaultdict
import itertools

import networkx as nx

class Operation(object):
    '''
        This class represents nodes in the directed-graph representation
    of the pipeline workflow.  Nodes have inputs and outputs which determine
    how the directed-graph is constructed.
    inputs: A list of hashable elements
    outputs: A list of hashable elements
    '''
    def __init__(self, inputs, outputs, name=None):
        if name is None:
            name = uuid.uuid4()
        inputs = set(inputs)
        outputs = set(outputs)
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.modifies = inputs.intersection(outputs)
        self.originates = outputs - inputs
        self.finalizes = inputs - outputs

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self)

class RootOperation(Operation):
    def __init__(self, outputs):
        Operation.__init__(self, [], outputs, name='Root')

def find_dependencies(xputs):
    results = []
    for p, desc in xputs.items():
        results += list(itertools.product(desc['originated_by'], 
                desc['modified_by']))
        results += list(itertools.product(desc['modified_by'],
                desc['finalized_by']))
        results += list(itertools.product(desc['originated_by'],
                desc['finalized_by']))
    return results

def streamline_graph(graph, operations):
    '''
        Return a new streamlined graph that is just like graph, but removes 
    redundant edges.
    '''
    s_graph = nx.DiGraph()
    ordered_nodes = nx.topological_sort(graph)[::-1]
    print ordered_nodes 
    for i in range(len(ordered_nodes)-1):
        if isinstance(ordered_nodes[i], RootOperation):
            break
        s_graph.add_node(ordered_nodes[i])
        for nput in ordered_nodes[i].inputs:
            for j in range(i+1, len(ordered_nodes)):
                print ordered_nodes[i], ordered_nodes[j], nput, ordered_nodes[j].outputs
                if nput in ordered_nodes[j].outputs:
                    s_graph.add_edge(ordered_nodes[j], ordered_nodes[i])
                    break
    return tidy_graph(s_graph)

def plot_graph(graph, executing_operations=None, finished_operations=None, 
        colors=['gray', 'g', 'c'], layout='circular', **kwargs):
    pos = {'circular':nx.layout.circular_layout(graph),
            'spring':nx.layout.spring_layout(graph, iterations=500)}
    # determine the color of the nodes
    if executing_operations is None:
        executing_operations = []
    if finished_operations is None:
        finished_operations = []
    node_color = []
    for op in graph.nodes():
        color = colors[0]
        if op in executing_operations:
            color = colors[1]
        elif op in finished_operations:
            color = colors[2]
        node_color.append(color)

    nx.draw(graph, pos=pos[layout], node_color=node_color, **kwargs)

def tidy_graph(graph):
    '''Remove impossible operations and orphans that have no edges.'''
    impossible_operations = []
    to_be_removed = [None]
    while to_be_removed:
        for node in to_be_removed:
            if node is not None:
                print 'removing %s' % node
                graph.remove_node(node)
        to_be_removed = []
        for node in graph.nodes_iter():
            if graph.in_degree(node) == 0 and\
                    not isinstance(node, RootOperation):
                print node, isinstance(node, RootOperation)
                to_be_removed.append(node)
                impossible_operations.append(node)

    return graph, impossible_operations

class Scheduler(object):
    def __init__(self):
        self.operations = []
        self.root_operation = RootOperation([])
        self._originated_outputs = set()

    @property
    def ordered_operations(self):
        g = self.build_graph()
        return nx.topological_sort(g)

    def add_operation(self, new_op):
        # enforce the one-originator rule.
        violations = new_op.originates.intersection(self._originated_outputs)
        if violations:
            raise OneOriginatorError('You may not add the Operation "%s" since it originates %s which is(are) already originated by other Operations.')

        self.operations.append(new_op)
        self._originated_outputs.update(new_op.originates)

    def build_graph(self):
        xputs = self._find_xputs()
        dependencies = find_dependencies(xputs)

        graph = nx.DiGraph()
        map(graph.add_node, self.operations)
        map(graph.add_edge, *zip(*dependencies))
        return graph

    def set_root_outputs(self, outputs):
        self.root_operation = RootOperation(outputs)
        to_be_removed = []
        for op in self.operations:
            if op.originates.intersection(self.root_operation.originates):
                to_be_removed.append(op)
        for rop in to_be_removed:
            self.operations.remove(rop)

    def _find_xputs(self):
        '''
            Return xputs, which is a nested dictionary of lists that
        describe the data-flow for inputs and outputs.
        xputs[<input-or-output>]['originated_by'] = list of operations
                                ['modified_by'] = list of operations
                                ['finalized_by'] = list of operations
        '''
        xputs = defaultdict(lambda:{'originated_by':[], 
                'modified_by':[], 'finalized_by':[]})
        for op in self.operations + [self.root_operation]:
            for p in op.originates:
                xputs[p]['originated_by'].append(op)
            for p in op.modifies:
                xputs[p]['modified_by'].append(op)
            for p in op.finalizes:
                xputs[p]['finalized_by'].append(op)
        return xputs




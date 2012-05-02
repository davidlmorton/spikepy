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

import numpy
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
        if len(desc['modified_by']) == 0: 
            results += list(itertools.product(desc['originated_by'],
                    desc['finalized_by']))
    return results

def get_ready_operations(graph):
    '''
        Return the set of ready operations.  In order for an
    operation to be ready, it must have no incomming links.
    '''
    return [node for node in graph.nodes() if graph.in_degree(node) == 0]

def remove_operations(graph, operations):
    for op in operations:
        graph.remove_node(op)

def get_ready_sets(graph):
    g = graph.copy()
    nodes = {}
    for node in graph.nodes():
        nodes[node.name] = node

    operations = get_ready_operations(g)
    results = []
    while operations:
        results.append([nodes[op.name] for op in operations])
        remove_operations(g, operations)
        operations = get_ready_operations(g)
    return results
    

def layout_operations(graph, offset=None):
    ready_sets = get_ready_sets(graph)

    if offset is None:
        offset = numpy.array([1.0, 0.5])
    adjustment = numpy.sin(numpy.linspace(0.0, 2.0*numpy.pi, len(ready_sets)))
    positions = {}
    for x, rs in enumerate(ready_sets):
        names = sorted([op.name for op in rs])
        for op in rs:
            y = names.index(op.name)
            positions[op] = numpy.array([x+1, y+1+adjustment[x]])*offset
        
    return positions
        
def plot_graph(graph, executing_operations=None, finished_operations=None, 
        colors=['gray', 'g', 'c'], layout='circular', **kwargs):
    pos = {'circular':nx.layout.circular_layout(graph),
            'spring':nx.layout.spring_layout(graph, iterations=500),
            'linear':layout_operations(graph)}
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
    
    edge_color = []
    for f, t in graph.edges():
        color = 'k'
        if f in finished_operations:
            color = colors[2]
        edge_color.append(color)

    return nx.draw(graph, pos=pos[layout], edge_color=edge_color, 
            node_color=node_color, **kwargs)

def get_impossible_operations(operations):
    '''
        Return the list of operations that have inputs that
    are not originated by any other operation.
    '''
    xputs = get_xputs(operations) 

    impossible_operations = set()
    for info in xputs.values():
        if info['modified_by'] and not info['originated_by']:
            impossible_operations.update(info['modified_by'])
        if info['finalized_by'] and not info['originated_by']:
            impossible_operations.update(info['finalized_by'])
    return impossible_operations 


def get_xputs(operations):
    '''
        Return xputs, which is a nested dictionary of lists that
    describe the data-flow for inputs and outputs.
    xputs[<input-or-output>]['originated_by'] = list of operations
                            ['modified_by'] = list of operations
                            ['finalized_by'] = list of operations
    '''
    xputs = defaultdict(lambda:{'originated_by':[], 
            'modified_by':[], 'finalized_by':[]})
    for op in operations:
        for p in op.originates:
            xputs[p]['originated_by'].append(op)
        for p in op.modifies:
            xputs[p]['modified_by'].append(op)
        for p in op.finalizes:
            xputs[p]['finalized_by'].append(op)
    return xputs


class Scheduler(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._operations = []
        self.root_operation = RootOperation([])
        self._originated_outputs = set()
        self._graph = None
        self._display_graph = None
        self._impossible_operations = None
        self._executing_operations = set()
        self._finished_operations = set()

    def _setup_graphs(self):
        self._graph, self._impossible_operations = self.build_graph()
        self._display_graph = self.build_graph()[0]

    @property
    def ready_operations(self):
        if self._graph is None:
            self._setup_graphs()
        return get_ready_operations(self._graph)

    @property
    def impossible_operations(self):
        if self._impossible_operations is None:
            self._setup_graphs()
        return self._impossible_operations

    @property
    def operations(self):
        return self._operations
        
    def start_operation(self, operation):
        self._executing_operations.add(operation)

    def complete_operation(self, operation):
        self._executing_operations.remove(operation)
        self._finished_operations.add(operation)
        remove_operations(self._graph, [operation])

    def plot(self, layout='linear', **kwargs):
        return plot_graph(self._display_graph, 
                finished_operations=self._finished_operations, 
                executing_operations=self._executing_operations, 
                        layout=layout, **kwargs)

    def add_operation(self, new_op):
        # enforce the one-originator rule.
        violations = new_op.originates.intersection(self._originated_outputs)
        if violations:
            raise OneOriginatorError('You may not add the Operation "%s" since it originates %s which is(are) already originated by other Operations.')

        self._operations.append(new_op)
        self._originated_outputs.update(new_op.originates)

    def build_graph(self):
        operations = self._operations + [self.root_operation]
        impossible_operations = set()
        while True:
            tio = get_impossible_operations(operations)
            impossible_operations.update(tio)
            if tio:
                for io in tio:
                    operations.remove(io)
            else:
                break

        xputs = get_xputs(operations)
        dependencies = find_dependencies(xputs)

        graph = nx.DiGraph()
        map(graph.add_node, operations)
        if dependencies:
            map(graph.add_edge, *zip(*dependencies))
        return graph, impossible_operations 

    def set_root_outputs(self, outputs):
        '''
            Sets the root_operation's outputs and removes any of the operations
        in self._operations that originated those outputs.
        Returns:
            list of removed operations
        '''
        self.root_operation = RootOperation(outputs)
        to_be_removed = []
        for op in self._operations:
            if op.originates.intersection(self.root_operation.originates):
                to_be_removed.append(op)
        for rop in to_be_removed:
            self._operations.remove(rop)
        return to_be_removed


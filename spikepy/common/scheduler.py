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
import copy
import uuid
from collections import defaultdict
import itertools
from exceptions import Exception

import numpy

class OperationError(Exception):
    pass


class Operation(object):
    '''
        This class represents nodes in the directed-graph representation
    of the scheduled workflow.  Nodes have inputs and outputs which determine
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
        self.points_at = set()
        self.is_pointed_at_by = set()

    def point_at(self, other):
        if self is other:
            raise OperationError('An operation cannot point at itself.')
        self.points_at.add(other)
        other.is_pointed_at_by.add(self)

    def unpoint(self):
        '''
            Remove all incomming and outgoing links from this operation
        '''
        for other in self.points_at:
            other.is_pointed_at_by.remove(self)
        for other in self.is_pointed_at_by:
            other.points_at.remove(self)
        self.points_at = set()
        self.is_pointed_at_by = set()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s->%s->%s' % (
                str(list(self.inputs)).replace('[','(').replace(']',')'), 
                self.name, 
                str(list(self.outputs)).replace('[','(').replace(']',')'))


class RootOperation(Operation):
    def __init__(self, outputs):
        Operation.__init__(self, [], outputs, name='Root')


def find_dependencies(xputs):
    '''
        Return a list of (from, to) dependencies meaning that
    <to> depends directly on <from>.
    '''
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


def find_ready_operations(operations):
    '''
        Return the set of ready operations.  In order for an
    operation to be ready, it must have no incomming links.
    '''
    return [op for op in operations if len(op.is_pointed_at_by) == 0]


def clear_impossible_operations(operations):
    '''
        Removes impossible operations and return the set of removed operations.
    '''
    impossible_operations = set()
    while True:
        tio = find_impossible_operations(operations)
        impossible_operations.update(tio)
        if tio:
            for io in tio:
                operations.remove(io)
        else:
            break
    return impossible_operations 


def point_operations(operations):
    '''
        Create the links of the dependency graph by pointing the operations
    at each other.
    '''
    # initialize operations
    for op in operations:
        op.unpoint()

    xputs = find_xputs(operations)
    dependencies = find_dependencies(xputs)

    for source, target in dependencies:
        source.point_at(target)
            



def remove_operations(operations, to_be_removed):
    '''
        Remove a set of operations from the list of operations and
    unpoint them.
    '''
    for rop in to_be_removed:
        rop.unpoint()
        operations.remove(rop)


def find_ready_sets(operations):
    '''
        Return a list of sets of operations.  These sets represent
    all the operations that are available to run.  That is, when one
    set has completed, any of the operations in the next set is 
    available to be run.  (used by layout_operations).
    '''
    nodes = copy.deepcopy(operations)

    rops = find_ready_operations(nodes)
    results = []
    while rops:
        results.append(rops)
        remove_operations(nodes, rops)
        rops = find_ready_operations(nodes)
    return results
    

def layout_operations(operations, offset=None):
    '''
        Return a dictionary keyed on the operations and with
    values specifying the x-y position where they should be plotted.
    '''
    ready_sets = find_ready_sets(operations)

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
        

def plot_operations(plot_dict, axes):
    plot_links(plot_dict, axes)
    plot_nodes(plot_dict, axes)
    plot_labels(plot_dict, axes)


def plot_links(plot_dict, axes):
    thin_links = []
    thick_links = []
    thin_properties = []
    thick_properties = []

def find_impossible_operations(operations):
    '''
        Return the set of operations that have inputs that
    are not originated by any other operation.
    '''
    xputs = find_xputs(operations) 

    impossible_operations = set()
    for info in xputs.values():
        if info['modified_by'] and not info['originated_by']:
            impossible_operations.update(info['modified_by'])
        if info['finalized_by'] and not info['originated_by']:
            impossible_operations.update(info['finalized_by'])
    return impossible_operations 


def find_xputs(operations):
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
    '''
        This class represents a set of operations that may depend
    on each other and need to be scheduled to run in an order where
    these dependencies are met.

    Typical Usage:
        s = Scheduler()
        s.add_operation(<operation>) # repeat
        s.set_root_outputs(<outputs>)

        while s.operations:
            ready_operation = random.choice(s.ready_operations)
            s.start_operation(ready_operation)

            finished_operations = some_fn()
            for op in finished_operations:
                s.finish_operation(op)
    '''
    def __init__(self):
        self.reset()

    def reset(self):
        self._operations = set()
        self._display_operations = None
        self._started_operations = set()
        self._finished_operations = set()
        self._impossible_operations = None

        self._root_operation = RootOperation([])
        self._originated_outputs = set()

    @property
    def ready_operations(self):
        if self._display_operations is None:
            self._construct_graph()
        potentials = set(find_ready_operations(self._operations))
        potentials.difference_update(self._started_operations)
        return list(potentials)

    @property
    def impossible_operations(self):
        if self._display_operations is None:
            self._construct_graph()
        return self._impossible_operations

    @property
    def operations(self):
        return self._operations
        
    def start_operation(self, operation):
        self._started_operations.add(operation)

    def finish_operation(self, operation):
        self._started_operations.remove(operation)
        self._finished_operations.add(operation)
        operation.unpoint()
        if operation in self._operations:
            self._operations.remove(operation)

    def get_plot_info(self):
        '''
            Return a dictionary that can be used to 
        plot the scheduled operations.  The dictionary
        is keyed on the operations and has dictionaries
        as the values which describe how the operations and
        the links should be plotted.
        '''
        pass

    def add_operation(self, new_op):
        # enforce the one-originator rule.
        violations = new_op.originates.intersection(self._originated_outputs)
        if violations:
            raise OneOriginatorError('You may not add the Operation "%s" since it originates %s which is(are) already originated by other Operations.' % (new_op, new_op.originates))

        self._operations.add(new_op)
        self._originated_outputs.update(new_op.originates)

    def _construct_graph(self):
        '''
            Point the operations at one another according to their
        dependencies.  This may result in impossible operations which
        are then stored in self._impossible_operations.  This also
        originates self._display_operations which is a copy of the
        operations after they have been pointed properly.
        '''
        operations = self._operations.union(set([self._root_operation]))

        impossible_operations = clear_impossible_operations(operations)
        point_operations(operations)

        self._display_operations = copy.deepcopy(operations)

        self._root_operation.unpoint()
        self._impossible_operations = impossible_operations
        return operations, impossible_operations 

    def set_root_outputs(self, outputs):
        '''
            Sets the root_operation's outputs and removes any of the operations
        in self._operations that originated those outputs.
        Returns:
            list of removed operations
        '''
        self._root_operation = RootOperation(outputs)
        to_be_removed = []
        for op in self._operations:
            if op.originates.intersection(self._root_operation.originates):
                to_be_removed.append(op)
        for rop in to_be_removed:
            self._operations.remove(rop)
        return to_be_removed


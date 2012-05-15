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
    '''
    def __init__(self, inputs, outputs, name=None):
        '''
        Inputs:
            inputs: A list of hashable elements
            outputs: A list of hashable elements
            *kwargs*
            name: A string describing the operation
        '''
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
        '''
            Point this operation at another operation.  Raises OperationError
        if the other operation is this operation.
        '''
        if self is other:
            raise OperationError('An operation cannot point at itself.')
        self.points_at.add(other)
        other.is_pointed_at_by.add(self)

    def unpoint(self):
        '''
            Remove all incomming and outgoing links from this operation.  Also
        ensure that no operations point to this operation anymore.
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

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        for attr in ['name', 'inputs', 'outputs']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __ne__(self, other):
        return not self == other


class RootOperation(Operation):
    def __init__(self, outputs):
        Operation.__init__(self, [], outputs, name='Root')


# ---- Operation Functions ----
def find_xputs(operations):
    '''
        Return xputs, which is a nested dictionary of lists that
    describe the data-flow for inputs and outputs.

    Inputs:
        operations: a set or list of Operation objects
    Returns:
        xputs: a dictionary of dictionaries of lists of operations...

        xputs[<input-or-output>]['originated_by'] = set of operations
                                ['modified_by'] = set of operations
                                ['finalized_by'] = set of operations
    '''
    xputs = defaultdict(lambda:{'originated_by':set(), 
            'modified_by':set(), 'finalized_by':set()})
    for op in operations:
        for p in op.originates:
            xputs[p]['originated_by'].add(op)
        for p in op.modifies:
            xputs[p]['modified_by'].add(op)
        for p in op.finalizes:
            xputs[p]['finalized_by'].add(op)
    return xputs


def find_dependencies(xputs):
    '''
        Return a list of (from, to) dependencies meaning that
    <to> depends directly on <from>.
    Inputs:
        xputs: the output of the find_xputs() function
    Returns:
        dependencies: a set of tuples of Operation objects
    '''
    dependencies = set()
    for p, desc in xputs.items():
        dependencies.update(list(itertools.product(desc['originated_by'], 
                desc['modified_by'])))
        dependencies.update(list(itertools.product(desc['modified_by'],
                desc['finalized_by'])))
        if len(desc['modified_by']) == 0: 
            dependencies.update(list(itertools.product(desc['originated_by'],
                    desc['finalized_by'])))
    return dependencies


def point_operations(operations):
    '''
        Create the links of the dependency graph by pointing the operations
    at each other.  The dependencies are determined by calling find_xputs
    and find_dependencies.

    Inputs:
        operations: a set of Operation objects
    Returns:
        None (modifies the Operation objects in <operations>)
    '''
    xputs = find_xputs(operations)
    dependencies = find_dependencies(xputs)

    for source, target in dependencies:
        source.point_at(target)


def find_impossible_operations(operations):
    '''
        Return the set of operations that have inputs that
    are not originated by any other operation.
    Inputs:
        operations: a set or list of Operation objects
    Returns:
        impossible_operations: a set of Operation objects
    '''
    xputs = find_xputs(operations) 

    impossible_operations = set()
    for info in xputs.values():
        if info['modified_by'] and not info['originated_by']:
            impossible_operations.update(info['modified_by'])
        if info['finalized_by'] and not info['originated_by']:
            impossible_operations.update(info['finalized_by'])
    return impossible_operations 


def clear_impossible_operations(operations):
    '''
        Removes impossible operations and return the set of removed operations.
    Inputs:
        operations: a list or set of Operation objects
    Returns:
        impossible_operations: the list of operations removed from <operations>
                because they were impossible
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


def find_ready_operations(operations):
    '''
        Return the set of ready operations.  In order for an
    operation to be ready, it must have no incomming links.
    Inputs:
        operations: a set or list of Operation objects
    Returns:
        ready_operations: a list of operations that are ready
    '''
    return set([op for op in operations if len(op.is_pointed_at_by) == 0])


def remove_operations(operations, to_be_removed):
    '''
        Remove a set of operations from the list (or set) of operations 
    provided and unpoint them.

    Inputs:
        operations: a set or list of Operation objects
        to_be_removed: another set or list of Operation objects that should
                be removed from <operations>
    Returns:
        None (<operations> is modified)
    '''
    for rop in to_be_removed:
        operations.remove(rop)
        rop.unpoint()

def copy_operation_set(operations):
    '''
        Make and return a copy of the list of <operations> provided.  The
    points_at and is_pointed_at_by variables are also taken care of, so that
    the copies point to their copied counterparts.  It is important though that
    no operations point_to or are pointed_at_by any operations that are not
    in the <operations> provided.

    Inputs:
        operations: a list or set of Operation objects
    Returns:
        new_operations: a set of operations that are copies of the
                <operations> provided.
        old_to_new: a dictionary keyed on old operations and valued with
                new operations
        new_to_old: a dictionary keyed on new operations and valued with
                old operations
    '''
    new_ops = {}
    old_ops = {}
    for op in operations:
        new_op = Operation(op.inputs, op.outputs, op.name)
        new_ops[op] = new_op 
        old_ops[new_op] = op

    for nop in new_ops.values():
        old_op = old_ops[nop]
        points_at = [new_ops[op] for op in old_op.points_at]
        is_pointed_at_by = [new_ops[op] for op in old_op.is_pointed_at_by]
        nop.points_at = set(points_at)
        nop.is_pointed_at_by = set(is_pointed_at_by)

    return set(new_ops.values()), new_ops, old_ops


def find_ready_sets(operations):
    '''
        Return a list of sets of operations.  These sets represent
    all the operations that are available to run.  That is, when one
    set has completed, any of the operations in the next set is 
    available to be run.  (used by layout_operations).
    
    Inputs:
        operations: a set or list of Operation objects
    Returns:
        ready_sets: a list of sets of Operation objects (copies of those 
                in <operations>)
    '''
    nodes, new_index, old_index = copy_operation_set(operations)

    rops = find_ready_operations(nodes)
    results = []
    while rops:
        results.append([old_index[rop] for rop in rops])
        remove_operations(nodes, rops)
        rops = find_ready_operations(nodes)
    return results
    

def layout_operations(operations, offset=None):
    '''
        Return a dictionary keyed on the operations and with
    values specifying the x-y position where they should be plotted.

    Inputs:
        operations: a set or list of Operation objects
        *kwarg*
        offset: a 2d numpy array of floats describing the distance between 
                operations in the x and y directions respectively.
    Returns:
        positions: a dictionary of (x, y) pairs for each operation in 
                <operations>
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
        self._graph = None
        self._display_graph = None
        self._started_operations = set()
        self._finished_operations = set()
        self._impossible_operations = None

        self._root_operation = RootOperation([])
        self._originated_outputs = set()

    def get_ready_operations(self):
        if self._graph is None:
            self._construct_graph()
        potentials = find_ready_operations(self._graph)
        potentials.difference_update(self._started_operations)
        return list(potentials)

    @property
    def impossible_operations(self):
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
            self._graph.remove(operation)

    def get_plot_dict(self):
        '''
            Return a dictionary that can be used to plot the scheduled 
        operations.  The dictionary is keyed on the operations and has 
        dictionaries as the values which describe how the operations and 
        the links should be plotted.
        '''
        fill_colors = {'started':'cyan', 'finished':'black', 'default':'white'}
        edge_colors = {'started':'black', 'finished':'cyan', 'default':'black'}

        positions = layout_operations(self._display_graph)

        verts = numpy.array([(0.0, 0.0), (1.0, -1.0), (8.0, -1.0), 
                             (9.0, 0.0), (9.0, 3.0), (8.0, 4.0), 
                             (1.0, 4.0), (0.0, 3.0), (0.0, 0.0)])
        verts -= numpy.average(verts, axis=0)
        verts = [v for v in verts]

        plot_dict = {}
        links = []
        xs = []
        ys = []
        edgecolors = []
        facecolors = []
        labels = []
        for op in positions.keys():
            graph_op = self._graph_index[op]
            state = 'default'
            if graph_op in self._started_operations:
                state = 'started'
            if graph_op in self._finished_operations:
                state = 'finished'
            color = edge_colors[state]
            edgecolors.append(color)
            facecolors.append(fill_colors[state])
            xs.append(positions[op][0])
            ys.append(positions[op][1])
            labels.append((xs[-1], ys[-1], op.name, 
                    {'color':color, 'zorder':3, 
                     'horizontalalignment':'center',
                     'verticalalignment':'center'}))
            for other in op.points_at:
                x = (positions[op][0], positions[other][0])
                y = (positions[op][1], positions[other][1])
                kwargs = {'color':color, 'linewidth':1, 'zorder':1}
                links.append((x, y, kwargs))

                mid_x = (numpy.average(x), x[1])
                mid_y = (numpy.average(y), y[1])
                kwargs = {'color':color, 'linewidth':3, 'zorder':1}
                links.append((mid_x, mid_y, kwargs))
        plot_dict['link_list'] = links
        
        plot_dict['node_info'] = {'xs':xs, 'ys':ys, 'kwargs':{'verts':verts, 'marker':None, 'edgecolors':edgecolors, 'facecolors':facecolors, 's':600, 'zorder':2}}
        plot_dict['label_list'] = labels
        return plot_dict 


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
        dependencies(see point_operations).  This may result in impossible 
        operations which are then stored in self._impossible_operations.
        
        Inputs:
            None
        Returns:
            impossible_ops: a set of Operations that couldn't be included in
                    the dependency graph because they didn't depend on the
                    RootOperation (self._root_operation).
        Modifies:
            self._impossible_operations: see <impossible_ops> above
            self._graph: a subset of self._operations that are included in
                    the dependency graph.
            self._display_graph: a copy of self._graph but also includes
                    a copy of the RootOperation. (used for visualization)
        '''
        self._graph = copy.copy(self._operations)
        operations = self._operations.union(set([self._root_operation]))

        impossible_operations = clear_impossible_operations(operations)
        point_operations(operations)

        self._display_graph, self._display_index, self._graph_index =\
                copy_operation_set(operations)
        self.start_operation(self._root_operation)
        self.finish_operation(self._root_operation)

        self._impossible_operations = impossible_operations
        return impossible_operations 

    def set_root_outputs(self, outputs):
        '''
            Sets the root_operation's outputs and removes any of the operations
        in self._operations that originated those outputs.
        Inputs:
            outputs: a list or set of outputs that the RootOperation should have
        Returns:
            removed_ops: list of removed operations (Removed because they 
                    originated the same outputs as the new RootOperation.)
        Modifies:
            self._operations: removes <removed_ops> above
        '''
        self._root_operation = RootOperation(outputs)
        to_be_removed = []
        for op in self._operations:
            if op.originates.intersection(self._root_operation.originates):
                to_be_removed.append(op)
        for rop in to_be_removed:
            self._operations.remove(rop)
        return to_be_removed


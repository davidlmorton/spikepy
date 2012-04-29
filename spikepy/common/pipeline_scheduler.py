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

def score_operations(operations, available_outputs):
    '''
        Give each operation a prioritization score (lower-is-better), based
    on how many of the outputs it originates are inputs to other operations.
    That is, how many other operations will this operation make possible.
    Returns:
        sorted_operations
        scores
    '''
    # operations that modify an available_output are given lowest score.
    modifying_offset = -len(operations)*100000 

    sorting_list = []
    for op in operations:
        score = -sum([len(oop.inputs.intersection(op.originates)) 
                for oop in operations])
        if op.modifies.intersection(available_outputs):
            score += modifying_offset
        sorting_list.append((score, op))

    sorting_list.sort()
    return ([op for score, op in sorting_list],
            [score for score, op in sorting_list])


def find_insertable_operation(operations, available_outputs):
    '''
        Return the first insertable operation found in operations.  To be
    insertable, an operation must have only inputs that are in 
    available_outputs.
    '''
    for op in operations:
        if not (op.inputs - available_outputs):
            return op
    return None


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
        self.points_to = []
        self.is_pointed_at_by = []

    def point_at(self, target):
        self.points_to.append(target)
        target.is_pointed_at_by.append(self)

    def clear_links(self):
        self.points_to = []
        self.is_pointed_at_by = []

    def __str__(self):
        return str(self.name)

class PipelineScheduler(object):
    def __init__(self, root_operation=None):
        self.operations = []
        self.root_operation = root_operation
        self._originated_outputs = set()

    def add_operation(self, new_op):
        # enforce the one-originator rule.
        violations = new_op.originates.intersection(self._originated_outputs)
        if violations:
            raise OneOriginatorError('You may not add the Operation "%s" since it originates %s which is(are) already originated by other Operations.')

        self.operations.append(new_op)

    def _get_available_operations(self, available_outputs, operations):
        '''
            Return the list of operations that have not been put into the 
        graph, prioritized so that modifying operations come earlier than
        non-modifying operations.
        '''
        ungraphed_operations = [op for op in operations if not op.points_to]
        score_operations(ungraphed_operations)

    def build_graph(self):
        # clear old links (if they exist)
        for op in self.operations + [self.root_operation]:
            op.clear_links()

        available_outputs = self.root_operation.outputs
        finalized_outputs = set([])
        finalized_by = {} # what operation finalized the output.
        provided_by = {} # who currently provides what output.
        for output in self.root_operation.outputs:
            provided_by[output] = self.root_operation
            
        available_operations, scores = score_operations(self.operations, 
                available_outputs)

        while available_operations:
            # find operation that can be put into graph
            op = find_insertable_operation(available_operations, 
                    available_outputs)
            if op is None:
                raise ImpossibleOperationError(op)

            # put operation into graph
            print 'adding operation %s' % op
            violations = op.modifies.intersection(finalized_outputs)
            if violations:
                raise FinalizationError(op, violations, finalized_by)
            for i in op.inputs:
                op.point_at(provided_by[i])
                # update provided_by if this op modifies the input
                if i in op.modifies:
                    provided_by[i] = op
                # update finalized_by if this op fianlizes the input
                if i in op.finalizes:
                    finalized_by[i] = op
                    finalized_outputs.add(i)
            # update available_outputs
            for o in op.outputs:
                available_outputs.add(o)
            for o in op.originates:
                provided_by[o] = op

            # remove operation from available operations
            available_operations.remove(op)
            available_operations, scores = score_operations(
                    available_operations, available_outputs)

        
        

    
        


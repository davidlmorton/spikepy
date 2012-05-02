from scheduler import Scheduler, Operation

data = [([1],[2],'A'),
        ([2],[3],'B'),
        ([3],[3,4],'C'),
        ([2],[2,5],'D'),
        ([3,4],[3,4],'E'),
        ([1,2],[2],'F'),
        ([4,5], [4], 'G'),
        ([5], [6], 'H')
        ]

def make_operations(data):
    results = []
    for inputs, outputs, name in data:
        results.append(Operation(inputs, outputs, name))    
    return results

ps = Scheduler()
ps.set_root_outputs([1])
for operation in make_operations(data):
    ps.add_operation(operation)

ops = {}
for op in ps.operations:
    ops[op.name] = op
    

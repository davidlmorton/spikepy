from pipeline_scheduler import PipelineScheduler, Operation

data = [([1],[2],'A'),
        ([2],[3],'B'),
        ([3],[3,4],'C'),
        ([2],[2,5],'D'),
        ([3,4],[3,4],'E'),
        ([1,2],[2],'F'),
        ]

def make_operations(data):
    results = []
    for inputs, outputs, name in data:
        results.append(Operation(inputs, outputs, name))    
    return results

ps = PipelineScheduler(root_operation=Operation([],[1],'root'))
for operation in make_operations(data):
    ps.add_operation(operation)


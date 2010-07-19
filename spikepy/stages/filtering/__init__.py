import os

method_modules = []
method_names = []

this_file = __file__
this_dir = os.path.split(this_file)[0] 

files_in_this_dir = os.listdir(this_dir)
for file in files_in_this_dir:
    if (os.path.isdir(os.path.join(this_dir, file)) and 
        not file.startswith(".")):
        exec('from . import %s' % file)
        method_modules.append(eval(file))
        method_names.append(method_modules[-1].name.lower())

def get_method(method_name=None):
    if method_name is None:
        print "Method Names available are %s" % str(method_names)
        return
    index = method_names.index(method_name.lower())
    return method_modules[index]

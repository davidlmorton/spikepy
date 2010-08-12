from . import program_text as pt

def make_strategy(strategy_name, methods_used_dict, settings_dict):
    return_dict = {}
    return_dict[strategy_name] = {'methods_used':methods_used_dict, 
                                      'settings':settings_dict}
    return return_dict
    
def make_methods_set_name(strategy_name):
    return strategy_name.split('(')[0]

def make_settings_name(strategy_name):
    return strategy_name.split('(')[1][:-1]

def make_strategy_name(methods_set_name, settings_name):
    pre  = methods_set_name
    post = settings_name
    if len(pre) >= 1:
        new_name = pre[0].upper() + pre[1:].lower() + '(%s)' % post.lower()
    else:
        new_name = pt.INVALID
    return new_name


        

_class_registry = {}

force_unique_names = True

class unique_name_list(list):
    def __init__(self):
        list.__init__(self)

    def append(self, value):
        # get names of existing members
        existing_names = [cls().name for cls in self]
        if value().name not in existing_names:
            list.append(self, value)
        else:
            raise RuntimeError("A class with the name '%s' has already been registered." % value().name)

class RegisteringClass(type):
    def __init__(cls, name, bases, attrs):
        register = True
        if hasattr(cls, '_skips_registration'):
            register = not cls._skips_registration
            del cls._skips_registration
        if hasattr(cls, '_is_base_class'):
            if cls._is_base_class:
                if force_unique_names:
                    _class_registry[cls] = unique_name_list()
                else:
                    _class_registry[cls] = []
            del cls._is_base_class
        if register:
            for base_class in _class_registry.keys():
                if issubclass(cls, base_class) or base_class is cls:
                    _class_registry[base_class].append(cls)


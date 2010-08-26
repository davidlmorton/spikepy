_class_registry = {}

class RegisteringClass(type):
    def __init__(cls, name, bases, attrs):
        register = True
        if hasattr(cls, '_skips_registration'):
            register = not cls._skips_registration
            del cls._skips_registration
        if hasattr(cls, '_is_base_class'):
            if cls._is_base_class:
                _class_registry[cls] = []
            del cls._is_base_class
        if register:
            for base_class in _class_registry.keys():
                if issubclass(cls, base_class) or base_class is cls:
                    _class_registry[base_class].append(cls)


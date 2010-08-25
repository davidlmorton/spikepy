_class_registry = {}
_base_classes = {}

class RegisteringClass(type):
    def __init__(cls, name, bases, attrs):
        register = True
        if hasattr(cls, '_skips_registration'):
            register = not cls._skips_registration
            del cls._skips_registration
        if hasattr(cls, '_is_base_class'):
            if cls._is_base_class:
                _class_registry[name] = []
                _base_classes[name] = cls
            del cls._is_base_class
        if register:
            for base_class_name, base_class in _base_classes.items():
                if issubclass(cls, base_class):
                    _class_registry[base_class_name].append(cls)


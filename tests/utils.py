from functools import wraps

_Function = type(lambda: None)

def staticmethods(cls):
    """Make all of a class's methods static if they are not already."""
    for attr, value in vars(cls).items():
        if type(value) is _Function:
            setattr(cls, attr, staticmethod(value))
    return cls

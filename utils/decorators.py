import inspect
import logging
import os
from functools import wraps
from typing import Callable
from .logger import Logger


class TypeCheckLogger(Logger):
    LEVEL_DEFAULT = logging.ERROR
    LEVEL_WRITE_DEFAULT = logging.WARNING


def type_check(write_to_file: bool = False, file_path: str = "", ignore = []):
    
    def decorator(func: Callable) -> Callable:
        """
        Décorateur qui vérifie le type des arguments passés à une fonction
        
        Args:
            func (function): la fonction à décorer.
            
        Returns:
            function : la fonction décorée qui effectue la vérification de type avant l'appel à la fonction originale.
        """
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            
            if write_to_file and not os.path.exists(file_path):
                TypeCheckLogger.write_to_file(file_path)
            
            for name, value in bound_args.arguments.items():
                if name in ignore:
                    continue 
                
                arg_type = sig.parameters[name].annotation
                
                if arg_type != inspect.Parameter.empty and not isinstance(value, arg_type):
                    TypeCheckLogger.exception(f"Argument < {name} > doit être de type {arg_type}.")
                    return
                    
            return func(*args, **kwargs)
        return wrapper
    return decorator
import os
import inspect
import datetime

# Publicizing classes and methods to share important structures for an API.
# Publicity ensures all classes or methods are easily accessible, and if used,
# provide logging and error handling. 

class Public:
        def Class(public_class: type) -> type:
                class _Proxy:
                        def __call__(self, *positional_arguments: tuple, **keyword_arguments: dict) -> None:
                                frame   = inspect.currentframe().f_back
                                local   = frame.f_locals
                                cls     = local.get("self", "UNKNOWN").__class__.__name__
                                mtd     = frame.f_code.co_name
                                create_log("Public Class", cls, mtd)
                return _Proxy()

        def Method(public_method: type) -> type:
                def _Proxy(self, *positional_arguments: tuple, **keyword_arguments: dict) -> None:
                        frame           = inspect.currentframe().f_back
                        local           = frame.f_locals
                        cls             = local.get("self", "UNKNOWN").__class__.__name__
                        mtd             = frame.f_code.co_name
                        create_log("Public Method", cls, mtd)

                        return public_method(self, *positional_arguments, **keyword_arguments)
                return _Proxy

# Privating classes and methods to keep integrity within a build that sets up for an
# API. Important classes and methods that would comprimise data within our
# application.

class Private:
        def Class(private_class: type) -> None | type:
                class _Proxy(private_class):
                        def __new__(subclass, *positional_arguments, **keyword_arguments):
                                frame           = inspect.currentframe().f_back
                                global_agent    = frame.f_globals.get("__name__")

                                if global_agent != private_class.__module__:
                                        raise PermissionError

                                local           = frame.f_locals
                                cls             = local.get("self", "UNKNOWN").__class__.__name__
                                mtd             = frame.f_code.co_name
                                create_log("Private Class", cls, mtd)

                                return super().__new__(subclass, *positional_arguments, **keyword_arguments)

                _Proxy.__name__         = private_class.__name__
                _Proxy.__qualname__     = private_class.__qualname__
                _Proxy.__module__       = private_class.__module__

                return _Proxy

        def Method(private_method: type) -> None | type:
                def _Proxy(self, *positional_arguments: tuple, **keyword_arguments: dict) -> None:
                        frame           = inspect.currentframe().f_back
                        local           = frame.f_locals

                        if not isinstance(local.get("self", None), type(self)):
                                raise PermissionError

                        cls             = local.get("self", "UNKNOWN").__class__.__name__
                        mtd             = frame.f_code.co_name
                        create_log("Private Method", cls, mtd)

                        return private_method(self, *positional_arguments, **keyword_arguments)
                return _Proxy

os.makedirs("logs", exist_ok=True)

DATE_TIME_START                         = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def create_log(type_name: str, class_name: str, method_name: str) -> str:
        logs                            = open("logs/{}".format(DATE_TIME_START), "a")
        log                             = "[{}] [{}]: [               \n".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S"), type_name)
        log                            += "    'Calling Class': '{}'  \n".format(class_name)
        log                            += "    'Calling Method': '{}' \n".format(method_name)
        log                            += "]\n"
        logs.write(log)
        logs.close()
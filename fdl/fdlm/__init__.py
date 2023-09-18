import os
from fdl.helper import BindModuleHelper


def __register_fdlm():
    dir_path = os.path.dirname(__file__)
    file_names = os.listdir(dir_path)

    for name in file_names:
        if name == __file__:
            continue
        module_path = os.path.join(dir_path, name)
        binder = BindModuleHelper(module_path)
        binder.bind()


__register_fdlm()

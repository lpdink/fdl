import os

from fdl._utils import bind


def __register_fdlm():
    dir_path = os.path.dirname(__file__)
    file_names = os.listdir(dir_path)

    for name in file_names:
        if name == __file__:
            continue
        module_path = os.path.join(dir_path, name)
        bind(module_path)


__register_fdlm()

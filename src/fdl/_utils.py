import inspect
import json
import os
import re
import shutil
import sys
from collections import Counter
from copy import deepcopy
from datetime import datetime

FDL_OBJ = {"clazz": "NotSet"}


def setup_global_seed(seed):
    if seed is not None:
        import random

        import numpy as np
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)
        random.seed(seed)
        torch.backends.cudnn.deterministic = True


def is_json_serializable(obj):
    if isinstance(obj, (dict, list, tuple, str, int, float, bool, type(None))):
        return True
    else:
        return False


def gen_clazz_example_obj(clazz, clazz_name):
    obj_config = deepcopy(FDL_OBJ)
    obj_config["clazz"] = clazz_name
    def_path = inspect.getabsfile(clazz)
    obj_config["def_path"] = def_path
    # 获取clazz的构造函数签名
    sign = inspect.signature(clazz)
    args = dict()
    for parm_name, parm_obj in sign.parameters.items():
        # 有default先default，没有就填注解，再没有就写一般
        # default必须可以被json序列化
        if parm_obj.default is not inspect._empty and is_json_serializable(
            parm_obj.default
        ):
            args[parm_name] = parm_obj.default
        elif parm_obj.annotation is not inspect._empty:
            args[parm_name] = str(parm_obj.annotation)
        else:
            args[parm_name] = "Todo Here!"

    obj_config["args"] = args
    return obj_config


def assert_file_exists(file_path: str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"file {file_path} not found.")


def load_json_file_to_dict(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    try:
        dic = json.loads(content)
    except json.decoder.JSONDecodeError as error:
        raise RuntimeError(
            f"{json_file_path} decoder failed. this file's grammar may be wrong."
        ) from error
    return dic


def copy_if_not_exists(file_path: str, dst_dir: str):
    """拷贝file_path到dst_dir，如果dst_dir下没有同名文件的话

    Args:
        file_path (str): 源文件路径
        dst_dir (str): 目标文件夹路径

    Raises:
        FileNotFoundError: _description_
        NotADirectoryError: _description_
        FileExistsError: _description_

    Returns:
        _type_: _description_
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"copy file failed. origin file {file_path} not exists")
    if not os.path.isdir(dst_dir):
        raise NotADirectoryError(f"{dst_dir} is not a Directory")
    file_name = os.path.basename(file_path)
    dst_file_path = os.path.join(dst_dir, file_name)
    if os.path.exists(dst_file_path):
        raise FileExistsError(f"copy file failed. {dst_file_path} already exists.")
    # breakpoint()
    shutil.copyfile(file_path, dst_file_path)
    return True


def create_dirs_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        raise FileExistsError(f"create dir failed:'{dir_path}' already exists.")


def create_workfolder(saved_path, task_name):
    """创建工作目录，saved_path/task_name/time/"""
    save_abs_path = os.path.abspath(saved_path)

    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    work_dir = os.path.join(save_abs_path, task_name, now)
    create_dirs_if_not_exists(work_dir)
    return work_dir


def bind(module_path):
    """
    如果module_path是file，则file直接作为顶层绑定。
    如果module_path是folder，则倒入该folder
    """
    if module_path is None:
        return
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"fdl bind modules error. {module_path} not exists!")
    module_path = re.sub("/+$", "", module_path)
    dir_path = os.path.dirname(module_path)
    sys.path.append(dir_path)
    module_name = os.path.basename(module_path)
    module_name = re.sub(r"\.py$", "", module_name)
    try:
        exec(f"import {module_name} as _register_module_")
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "fdl bind modules error. This may caused by missing __init__.py file"
            f" pointer to file in modules. error msg:{error.msg}"
        ) from error
    except ImportError as error:
        raise ImportError(
            "fdl bind modules error. This may caused by wrong grammar in"
            f" {module_name}. error msg:{error.msg}"
        ) from error


def read_json_from_file(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        try:
            rst = json.load(file)
        except json.JSONDecodeError as error:
            raise json.JSONDecodeError(
                f"{json_path} is not a valid json file.{error.msg}",
                error.doc,
                error.pos,
            ) from error
    return rst


# def get_object_names(object_config):
#     # get name list in object or list^(object)
#     names = list()
#     if isinstance(object_config, dict):
#         if "name" in object_config.keys():
#             names.append(object_config["name"])
#         if "clazz" in object_config.keys() and "args" in object_config.keys():
#             args = object_config["args"]
#             names += get_object_names(args)
#     elif isinstance(object_config, list):
#         for item in object_config:
#             names += get_object_names(item)
#     return names


def check_objects(objects):
    """
    check_objects:
    - element in top objects must be dict
    - element in top objects must have key 'clazz', clazz value must be str
    - name of element in top objects can't repeat.
    """
    obj_names = []
    for obj_config in objects:
        if not isinstance(obj_config, dict):
            raise TypeError(
                f"element in 'objects' list expected to be dict, got {type(obj_config)}"
            )
        if "clazz" not in obj_config.keys():
            raise KeyError(
                "element in 'objects' list expected to have key 'clazz', got"
                f" {obj_config.keys()}"
            )
        if not isinstance(obj_config["clazz"], str):
            raise TypeError(
                "clazz of element in 'objects' list expected to be str, got"
                f" {type(obj_config['clazz'])}"
            )
        # only count top elements' name
        if "name" in obj_config.keys():
            obj_names.append(obj_config["name"])
    counter = Counter(obj_names)
    repeat = list()
    for name, times in counter.items():
        if times > 1:
            repeat.append(name)
    if len(repeat) > 0:
        raise ValueError(
            f"top element's name expected not repeat, {repeat} have repeat."
        )


def check_config_file(json_path):
    """
    check json file:
    - must exists
    - valid json
    - have objects
    """
    assert_file_exists(json_path)
    config = read_json_from_file(json_path)
    if isinstance(config, dict):
        if "objects" not in config.keys():
            raise KeyError(f"{json_path} is a dict, but no 'objects' found.")
        objects = config["objects"]
        if not isinstance(objects, list):
            raise TypeError(f"objects in {json_path} expected to be list.")
    elif isinstance(config, list):
        objects = config
    else:
        raise TypeError(
            f"json file top elements must be dict or list, got {type(config)}"
        )
    check_objects(objects)

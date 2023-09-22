import os
import re
import sys
import shutil
import json
import inspect
from datetime import datetime
from copy import deepcopy

FDL_OBJ = {
    "name": "NotSet",
    "clazz": "NotSet",
    "is_core": False,
}


def setup_global_seed(seed):
    if seed is not None:
        import torch
        import numpy as np
        import random

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
    obj_config["name"] = f"{clazz.__name__}.__example_obj__"
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
    with open(json_file_path, "r") as file:
        content = file.read()
    try:
        dic = json.loads(content)
    except json.decoder.JSONDecodeError:
        raise RuntimeError(
            f"{json_file_path} decoder failed. this file's grammar may be wrong."
        )
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


def create_workfolder(saved_path, program_name):
    """创建工作目录，saved_path/program_name/time/"""
    save_abs_path = os.path.abspath(saved_path)

    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    work_dir = os.path.join(save_abs_path, program_name, now)
    create_dirs_if_not_exists(work_dir)


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
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            f"fdl bind modules error. This may caused by missing __init__.py file pointer to file in modules. error msg:{e.msg}"
        )
    except ImportError as e:
        raise ImportError(
            f"fdl bind modules error. This may caused by wrong grammar in {module_name}. error msg:{e.msg}"
        )

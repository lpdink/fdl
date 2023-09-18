from fdl.factory import Factory
from fdl.common import Logger
from copy import deepcopy
import json
import inspect

FDL_JSON = {
    "program": {"name": "MyProgram", "saved_path": "./fdl_space"},
    "objects": [],
}

FDL_OBJ = {
    "name": "panda_obj",
    "clazz": "zoo.Panda",
    "is_core": False,
}


def parse_args(args):
    clazzs = args.clazzs
    output_path = args.output
    return clazzs, output_path


def is_json_serializable(obj):
    if isinstance(obj, (dict, list, tuple, str, int, float, bool, type(None))):
        return True
    elif hasattr(obj, "__dict__"):
        return True
    else:
        return False


def gen_json(args):
    logging = Logger()
    clazzs, output_path = parse_args(args)
    factory = Factory()
    name2clazz = factory.get_name2clazz()
    clazz_count = dict()
    output_json = deepcopy(FDL_JSON)
    for query_item in clazzs:
        if query_item in name2clazz.keys():
            obj_config = deepcopy(FDL_OBJ)
            count = clazz_count.get(query_item, 0)
            obj_name = f"{query_item}._obj_{count}"
            obj_clazz = query_item
            count += 1
            clazz_count[query_item] = count
            clazz = name2clazz[query_item]
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
            # 设置
            obj_config["name"] = obj_name
            obj_config["clazz"] = obj_clazz
            obj_config["args"] = args
            output_json["objects"].append(obj_config)
        else:
            logging.warning(
                f"can't find {query_item} in factory, won't dump it to json."
            )
    with open(output_path, "w") as file:
        json.dump(output_json, file, indent=4)
    logging.info(f"saved gen json to {output_path}")

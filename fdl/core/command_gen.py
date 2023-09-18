from fdl.factory import Factory
from fdl.common import Logger
from fdl.utils import gen_clazz_example_obj
from copy import deepcopy
import json

FDL_JSON = {
    "program": {"name": "MyProgram", "saved_path": "./fdl_space"},
    "objects": [],
}


def parse_args(args):
    clazzs = args.clazzs
    output_path = args.output
    return clazzs, output_path


def gen_json(args):
    logging = Logger()
    clazzs, output_path = parse_args(args)
    factory = Factory()
    name2clazz = factory.get_name2clazz()
    clazz_count = dict()
    output_json = deepcopy(FDL_JSON)
    for query_item in clazzs:
        if query_item in name2clazz.keys():
            count = clazz_count.get(query_item, 0)
            obj_name = f"{query_item}._obj_{count}"
            obj_clazz = query_item
            count += 1
            clazz_count[query_item] = count
            clazz = name2clazz[query_item]
            obj_config = gen_clazz_example_obj(clazz)
            # 设置
            obj_config["name"] = obj_name
            obj_config["clazz"] = obj_clazz
            output_json["objects"].append(obj_config)
        else:
            logging.warning(
                f"can't find {query_item} in factory, won't dump it to json."
            )
    with open(output_path, "w") as file:
        json.dump(output_json, file, indent=4)
    logging.info(f"saved gen json to {output_path}")

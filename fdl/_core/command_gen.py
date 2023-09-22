from fdl._factory import Factory
from fdl._common import Logger
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
    for clazz_name in clazzs:
        if clazz_name in name2clazz.keys():
            count = clazz_count.get(clazz_name, 0)
            obj_name = f"{clazz_name}._obj_{count}"
            obj_clazz = clazz_name
            count += 1
            clazz_count[clazz_name] = count
            clazz = name2clazz[clazz_name]
            obj_config = gen_clazz_example_obj(clazz, clazz_name)
            # 设置
            obj_config["name"] = obj_name
            obj_config["clazz"] = obj_clazz
            output_json["objects"].append(obj_config)
        else:
            logging.warning(
                f"can't find {clazz_name} in factory, won't dump it to json."
            )
    with open(output_path, "w") as file:
        json.dump(output_json, file, indent=4)
    logging.info(f"saved gen json to {output_path}")

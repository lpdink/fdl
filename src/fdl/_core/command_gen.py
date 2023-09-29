import json
from copy import deepcopy

from fdl._factory import Factory
from fdl._utils import gen_clazz_example_obj

FDL_JSON = {
    "objects": [],
}


def parse_args(args):
    clazzs = args.clazzs
    output_path = args.output
    return clazzs, output_path


def gen_json(args):
    clazzs, output_path = parse_args(args)
    factory = Factory()
    name2clazz = factory.get_name2clazz()
    clazz_count = dict()
    output_json = deepcopy(FDL_JSON)
    for clazz_name in clazzs:
        if clazz_name in name2clazz.keys():
            count = clazz_count.get(clazz_name, 0)
            obj_clazz = clazz_name
            count += 1
            clazz_count[clazz_name] = count
            clazz = name2clazz[clazz_name]
            obj_config = gen_clazz_example_obj(clazz, clazz_name)
            # 设置
            obj_config["clazz"] = obj_clazz
            output_json["objects"].append(obj_config)
        else:
            print(f"can't find {clazz_name} in factory, won't dump it to json.")
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output_json, file, indent=4)
    print(f"saved gen json to {output_path}")

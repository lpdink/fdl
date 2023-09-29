import inspect
import json

from fdl._factory import Factory
from fdl._utils import gen_clazz_example_obj


def print_module_v(clazz, clazz_name):
    example_json = gen_clazz_example_obj(clazz, clazz_name)
    doc = clazz.__doc__
    example_json = json.dumps(example_json, indent=2)
    print("below is a example config of this clazz.")
    print("=" * 20)
    print(example_json)
    print("=" * 20)
    print("below is this clazz's doc")
    print("=" * 20)
    print(doc)
    print("=" * 20)


def parse_args(args):
    clazz = args.clazz
    verbose = args.verbose
    return clazz, verbose


def show(args):
    input_clazz, verbose = parse_args(args)
    factory = Factory()
    name2clazz = factory.get_name2clazz()
    if not verbose:
        print("=============name:clazz=============")

    for key, value in name2clazz.items():
        if input_clazz in key:
            if verbose:
                print_module_v(value, key)
            else:
                print(key, value)
    # for clazz_name in clazz:
    #     if clazz_name in name2clazz.keys():
    #         clazz = name2clazz[clazz_name]
    #         print_module(clazz, clazz_name)

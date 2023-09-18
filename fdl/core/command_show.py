import inspect
import json
from fdl.factory import Factory
from fdl.utils import gen_clazz_example_obj


def print_module(clazz):
    example_json = gen_clazz_example_obj(clazz)
    source_code = inspect.getsource(clazz)
    example_json = json.dumps(example_json, indent=2)
    print("below is a example config of this clazz.")
    print("=" * 20)
    print(example_json)
    print("=" * 20)
    print("below is this clazz's source code")
    print("=" * 20)
    print(source_code)
    print("=" * 20)


def parse_args(args):
    clazzs = args.clazzs
    return clazzs


def show(args):
    clazzs = parse_args(args)
    factory = Factory()
    if len(clazzs) == 0:
        factory.print_register_clazzs()
        return
    name2clazz = factory.get_name2clazz()
    for clazz_name in clazzs:
        if clazz_name in name2clazz.keys():
            clazz = name2clazz[clazz_name]
            print_module(clazz)

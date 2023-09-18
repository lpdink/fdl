"""
提供三个注册：
register
register_as
register_all
"""
import inspect
import re
from types import FunctionType

__all__ = ["register", "register_as", "register_all"]


class Factory:
    instance = None
    init = False

    def __new__(cls):
        if Factory.instance is None:
            Factory.instance = super().__new__(cls)
        return Factory.instance

    def __init__(self) -> None:
        if Factory.init:
            return
        self._name2clazz = dict()
        self._clazz2name = dict()
        self._name2obj = dict()
        self._obj2name = dict()
        self._core_objs = list()
        Factory.init = True

    def _replace_args(self, obj):
        obj_name = obj["name"]
        obj_args = list()
        obj_args = obj.get("args", obj_args)
        pattern = r"\${(.+?)}"
        if isinstance(obj_args, list):
            obj_args_iter = enumerate(obj_args)
        elif isinstance(obj_args, dict):
            obj_args_iter = obj_args.items()
        else:
            raise TypeError(
                f"args type expected to be list or dict, got {type(obj_args)}, factory construct obj {obj_name}"
            )

        for arg_idx, arg_value in obj_args_iter:
            match = re.search(pattern, str(arg_value))
            if match:
                match_str = match.group(1)
                # 匹配到的obj必须已经被创建
                assert (
                    match_str in self._name2obj.keys()
                ), f"{match_str} not found in objs_pool, this may caused by wrong words in json or wrong objs order. Be careful that father obj should in front."
                obj_args[arg_idx] = self._name2obj[match_str]
        return obj_args

    def create(self, dic: dict):
        assert "objects" in dic.keys(), "to create objs, dic should have key 'objects'!"

        assert isinstance(dic["objects"], list), "dic['objects'] should be list-like."

        # 按照objects列表的反序创建对象
        for obj in dic["objects"][::-1]:
            assert isinstance(obj, dict)
            # clazz必须已经在factory中注册
            if not obj["clazz"] in self._name2clazz.keys():
                raise KeyError(
                    f"fdl create obj failed. factory can't find clazz {obj['clazz']}, maybe not register properly."
                )

            # 解析args，将${}替换为对象
            obj_args = self._replace_args(obj)

            # 改变args中占位符指向后，创建new_obj
            if isinstance(obj_args, list):
                new_obj = self._name2clazz[obj["clazz"]](*obj_args)
            elif isinstance(obj_args, dict):
                new_obj = self._name2clazz[obj["clazz"]](**obj_args)
            else:
                raise TypeError("never exec this line.")
            # 保存core对象
            if getattr(obj, "is_core", False):
                self._core_objs.append(new_obj)
            # 将构造配置附件给对象
            setattr(new_obj, "_init_config", obj)
            self._name2obj[obj["name"]] = new_obj
            self._obj2name[new_obj] = obj["name"]

    def get_core_objs(self):
        return self._core_objs

    def register(self, name, clazz):
        if name not in self._name2clazz.keys():
            self._name2clazz[name] = clazz
        else:
            raise RuntimeError(
                f"register name '{name}' already been used by class {self._name2clazz[name]}"
            )
        if clazz not in self._clazz2name.keys():
            self._clazz2name[clazz] = name
        else:
            raise RuntimeError(
                f"class '{clazz}' already register with name {self._clazz2name[clazz]}"
            )


def register(obj):
    factory = Factory()
    if isinstance(obj, FunctionType) or inspect.isclass(obj):
        module_name = inspect.getmodule(obj).__name__
        register_name = f"{module_name}.{obj.__name__}"
        factory.register(register_name, obj)
        return obj
    else:
        raise RuntimeError(f"Not supported type {type(obj)} for register")


def register_as(name):
    factory = Factory()
    if isinstance(name, str):

        def inside(clazz):
            factory.register(name, clazz)
            return clazz

        return inside
    else:
        raise RuntimeError(f"Not supported type {type(name)} to register")

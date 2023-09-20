"""
提供三个注册：
register
register_as
register_all
"""
import inspect
import re

__all__ = ["register", "register_as", "register_clazz_as_name"]


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

    def _replace_place_holder_with_dict_get(self, command):
        # Define the regular expression pattern to match "${obj}"
        pattern = r"\${(.*?)}"

        # Define the replacement function
        def replace(match):
            obj_name = match.group(1)
            if not obj_name in self._name2obj.keys():
                raise KeyError(
                    f"{obj_name} not found in objs_pool, this may caused by wrong words in json or wrong objs order. Be careful that father obj should in front."
                )
            return f"_name2obj.get('{obj_name}')"
            # return q_dict_name + "[" + obj + "]"

        # Use re.sub() to replace all occurrences of the pattern with the replacement function
        result = re.sub(pattern, replace, command)

        return result

    def _exec_command_to_get_obj(self, command_str):
        command_pattern = "@@(.*?)@@"
        sub_commands = re.findall(command_pattern, command_str)
        if len(sub_commands) > 1:
            raise RuntimeError(
                f"Only allowed one exec(...) in args value, got {command_str}"
            )
        sub = sub_commands[0]
        sub = f"ret={sub}"
        exec_rst = dict()
        try:
            exec(sub, {"_name2obj": self._name2obj}, exec_rst)
        except Exception as e:
            raise RuntimeError(f"exec sub command {sub} failed. msg:{e}") from e
        if "ret" in exec_rst.keys():
            return exec_rst["ret"]
        else:
            raise RuntimeError("Never run this line.")

    def _replace_args(self, obj):
        obj_name = obj["name"]
        obj_args = list()
        obj_args = obj.get("args", obj_args)
        if isinstance(obj_args, list):
            obj_args_iter = enumerate(obj_args)
        elif isinstance(obj_args, dict):
            obj_args_iter = obj_args.items()
        else:
            raise TypeError(
                f"args type expected to be list or dict, got {type(obj_args)}, factory construct obj {obj_name}"
            )

        for arg_idx, arg_value in obj_args_iter:
            # 1. 替换+执行：@@str(${obj_name})@@+@@"hello world！"@@-》先替换，再执行
            # 2. 替换 ${obj_name}-》替换成对象
            # 3. 字面量 123->可以走2的逻辑，保持不变。
            if isinstance(arg_value, str):
                match = re.search(r"\${(.+?)}", str(arg_value))
                if arg_value.count("@@") >= 2:
                    # 解析命令并执行
                    command_str = self._replace_place_holder_with_dict_get(arg_value)
                    target_obj = self._exec_command_to_get_obj(command_str)
                elif match:
                    # 直接替换
                    match_str = match.group(1)
                    assert (
                        match_str in self._name2obj.keys()
                    ), f"{match_str} not found in objs_pool, this may caused by wrong words in json or wrong objs order. Be careful that father obj should in front."
                    target_obj = self._name2obj[match_str]
                else:
                    target_obj = arg_value
            else:
                target_obj = arg_value
            obj_args[arg_idx] = target_obj
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

        # 反转core_objs
        self._core_objs.reverse()

    def get_core_objs(self):
        return self._core_objs

    def get_name2clazz(self):
        return self._name2clazz

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

    def print_register_clazzs(self):
        print("=============name:clazz=============")
        for name, clazz in self._name2clazz.items():
            print(f"{name}  :  {clazz}")
        print("====================================")


def register(obj):
    factory = Factory()
    if inspect.isclass(obj):
        module_name = inspect.getmodule(obj).__name__
        register_name = f"{module_name}.{obj.__name__}"
        factory.register(register_name, obj)
        return obj
    else:
        raise RuntimeError(f"Not supported type {type(obj)} for register")


def register_clazz_as_name(clazz, name):
    factory = Factory()
    if isinstance(name, str):
        factory.register(name, clazz)
    else:
        raise RuntimeError(f"Not supported type {type(name)} to register")


def register_module_clazzs(module, top_name):
    for clazz_name in dir(module):
        if not clazz_name.startswith("_"):
            clazz = getattr(module, clazz_name)
            if inspect.isclass(clazz):
                register_clazz_as_name(clazz, f"{top_name}.{clazz_name}")


def register_as(name):
    factory = Factory()
    if isinstance(name, str):

        def inside(clazz):
            factory.register(name, clazz)
            return clazz

        return inside
    else:
        raise RuntimeError(f"Not supported type {type(name)} to register")

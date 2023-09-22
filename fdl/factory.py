"""
factory的作用：
- 提供register功能，
- 提供clazz和obj存储库，
- 根据json构造对象，
- 提供查询core对象的方法。
memory->register->creator
Register && register function(register, register_as, register_module_)
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

    def create(self, config: dict):
        assert "objects" in config.keys()
        obj_configs = config["objects"]
        assert isinstance(obj_configs, list)
        # 反序构建
        for idx, obj_config in enumerate(obj_configs[::-1]):
            assert isinstance(obj_config, dict)
            # get suggest anme
            suggest_name = f"objects_{idx}"
            obj_name, new_obj = self.create_single_obj(obj_config, suggest_name)
            # 保存顶层对象
            self._save_obj(obj_name, new_obj)
            # 顶层object 可能拥有字段command
            if "command" in obj_config.keys() and isinstance(obj_config["command"], str):
                self._core_objs.append(new_obj)
        # 反转core对象
        self._core_objs.reverse()
            

    def create_single_obj(self, obj_config: dict, suggest_name):
        obj_name = self._get_obj_name(obj_config, suggest_name)
        obj_clazz = self._get_obj_clazz(obj_config)
        obj_args = self._get_obj_args(obj_config)
        new_obj = self._construct_obj(obj_clazz, obj_args)
        # 保存对象的初始化配置
        setattr(new_obj, "_init_config", obj_config)
        return obj_name, new_obj

    def _get_obj_name(self, obj_config: dict, suggest_name=None):
        if "name" not in obj_config.keys():
            if isinstance(suggest_name, str):
                obj_config["name"] = suggest_name
            else:
                raise ValueError(
                    f"can't match name for {obj_config}, no key name and suggest_name is not str {suggest_name}."
                )
        return obj_config["name"]

    def _get_obj_clazz(self, obj_config: dict):
        assert (
            "clazz" in obj_config.keys()
        ), f"no clazz in {obj_config} construct obj failed."
        clazz_name = obj_config["clazz"]
        if clazz_name in self._name2clazz.keys():
            clazz = self._name2clazz[clazz_name]
        else:
            raise KeyError(f"clazz {clazz_name} not register!")
        return clazz

    def _get_obj_args(self, obj_config: dict):
        args = list()
        args = obj_config.get("args", args)
        obj_name = self._get_obj_name(obj_config)
        args = self._preprocess_args(args, obj_name)
        return args

    def _preprocess_args(self, args, father_name):
        # 参数args是一个list或dict容器，正则化容器元素
        if isinstance(args, list):
            args_iter = enumerate(args)
        elif isinstance(args, dict):
            args_iter = args.items()
        else:
            raise TypeError(
                f"unexpected args type, expected list or dict, got {type(args)}"
            )
        for arg_key, arg_value in args_iter:
            """
            arg_value:
            ["${item}"]
            [{"name":..., "clazz":...}]
            {"name":"${item}", "msg":"@@${item}.get_msg()@@"} # no clazz
            {"clazz":"....", "args":""} # with clazz
            """
            if isinstance(arg_value, dict):
                if "clazz" in arg_value.keys():
                    # 有clazz走子对象构建
                    sub_obj_name, arg_value = self.create_single_obj(
                        arg_value, suggest_name=f"{father_name}.{arg_key}"
                    )
                else:
                    # 没有则递归再处理此子元素，递归出口至所有元素都是非容器
                    arg_value = self._preprocess_args(
                        arg_value, f"{father_name}.{arg_key}"
                    )
            elif isinstance(arg_value, list):
                arg_value = self._preprocess_args(arg_value, f"{father_name}.{arg_key}")
            elif isinstance(arg_value, str):
                match = re.search(r"\${(.+?)}", str(arg_value))
                if arg_value.count("@@") >= 2:
                    # 解析命令并执行
                    command_str = self._replace_place_holder_with_dict_get(arg_value)
                    arg_value = self._exec_command_to_get_obj(command_str)
                elif match:
                    # 直接替换
                    match_str = match.group(1)
                    assert (
                        match_str in self._name2obj.keys()
                    ), f"{match_str} not found in objs_pool, this may caused by wrong words in json or wrong objs order. Be careful that father obj should in front."
                    arg_value = self._name2obj[match_str]
            args[arg_key] = arg_value
        return args
    
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
    
    def _construct_obj(self, clazz, args):
        assert callable(clazz)
        if isinstance(args, list):
            obj = clazz(*args)
        elif isinstance(args, dict):
            obj = clazz(**args)
        else:
            raise TypeError(f"construct obj expected args be list or dict, got {type(args)}")
        return obj
    
    def _save_obj(self, obj_name, obj):
        if obj_name not in self._name2obj.keys():
            self._name2obj[obj_name]  = obj
        else:
            raise RuntimeError(f"factory save obj failed. obj_name {obj_name} already been used by {self._name2obj[obj_name]}")
        if obj not in self._obj2name.keys():
            self._obj2name[obj]  = obj_name
        else:
            raise RuntimeError(f"factory save obj failed. obj {obj} already been saved with name {self._obj2name[obj]}")
        
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

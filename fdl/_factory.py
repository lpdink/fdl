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
import sys
import traceback

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
            obj_name = obj_config.get("name", suggest_name)
            new_obj = self.create_single_obj(obj_config)
            # 保存顶层对象
            self._save_obj(obj_name, new_obj)
            # 顶层object 可能拥有字段method
            if "method" in obj_config.keys() and isinstance(obj_config["method"], str):
                self._core_objs.append(new_obj)
        # 反转core对象
        self._core_objs.reverse()

    def create_single_obj(self, obj_config: dict):
        obj_clazz = self._get_obj_clazz(obj_config)
        obj_args = self._get_obj_args(obj_config)
        new_obj = self._construct_obj(obj_clazz, obj_args)
        # 保存对象的初始化配置
        setattr(new_obj, "_init_config", obj_config)
        return new_obj

    def _get_obj_clazz(self, obj_config: dict):
        assert (
            "clazz" in obj_config.keys()
        ), f"no clazz in {obj_config} construct obj failed."
        clazz_name = obj_config["clazz"]
        if clazz_name in self._name2clazz:
            clazz = self._name2clazz[clazz_name]
        else:
            raise ValueError(f"clazz '{clazz_name}' not register!")
        return clazz

    def _get_obj_args(self, obj_config: dict):
        args = list()
        args = obj_config.get("args", args)
        args = self._preprocess_args(args)
        return args

    def _preprocess_args(self, args):
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
            if isinstance(arg_value, dict):
                if "clazz" in arg_value.keys():
                    # 有clazz走子对象构建
                    arg_value = self.create_single_obj(arg_value)
                else:
                    # 没有则递归再处理此子元素，递归出口至所有元素都是非容器
                    arg_value = self._preprocess_args(arg_value)
            elif isinstance(arg_value, list):
                arg_value = self._preprocess_args(arg_value)
            elif isinstance(arg_value, str):
                match = re.search(r"\${(.+?)}", str(arg_value))
                if arg_value.count("@@") >= 2:
                    # 解析命令并执行
                    command_str = self._replace_place_holder_with_dict_get(arg_value)
                    arg_value = self._exec_command_to_get_obj(command_str)
                elif match:
                    # 直接替换
                    match_str = match.group(1)
                    if not match_str in self._name2obj:
                        raise KeyError(
                            f"find ref object {match_str} failed, this may caused by"
                            " wrong words in json or wrong objs order. Be careful that"
                            " father obj should in front."
                        )
                    arg_value = self._name2obj[match_str]
            args[arg_key] = arg_value
        return args

    def _replace_place_holder_with_dict_get(self, command):
        # Define the regular expression pattern to match "${obj}"
        pattern = r"\${(.*?)}"

        # Define the replacement function
        def replace(match):
            obj_name = match.group(1)
            if not obj_name in self._name2obj:
                raise KeyError(
                    f"{obj_name} not found in objs_pool, this may caused by wrong words"
                    " in json or wrong objs order. Be careful that father obj should"
                    " in front."
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
        exec_rst = dict()
        try:
            exec(sub, {"_name2obj": self._name2obj}, exec_rst)  # pylint:disable=W0122
        except Exception as error:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_str = "".join(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            )
            raise RuntimeError(
                f"exec sub command '{sub}' failed. Exception:\n {traceback_str}"
            ) from error
        if "ret" in exec_rst:
            return exec_rst["ret"]
        else:
            raise KeyError(
                "ret is not set between @@@@, make sure set ret like: 'ret=None'"
            )

    def _construct_obj(self, clazz, args):
        assert callable(clazz)
        if isinstance(args, list):
            try:
                obj = clazz(*args)
            except Exception as error:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_str = "".join(
                    traceback.format_exception(exc_type, exc_value, exc_traceback)
                )
                raise RuntimeError(
                    f"construct clazz {clazz} with args {args} failed.  exception:\n"
                    f" {traceback_str}"
                ) from error
        elif isinstance(args, dict):
            try:
                obj = clazz(**args)
            except Exception as error:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_str = "".join(
                    traceback.format_exception(exc_type, exc_value, exc_traceback)
                )
                raise RuntimeError(
                    f"construct clazz {clazz} with args {args} failed.  exception:\n"
                    f" {traceback_str}"
                ) from error
        else:
            raise TypeError(
                f"construct obj expected args be list or dict, got {type(args)}"
            )
        return obj

    def _save_obj(self, obj_name, obj):
        if obj_name not in self._name2obj:
            self._name2obj[obj_name] = obj
        else:
            raise RuntimeError(
                f"factory save obj failed. obj_name {obj_name} already been used by"
                f" {self._name2obj[obj_name]}"
            )
        if obj not in self._obj2name:
            self._obj2name[obj] = obj_name
        else:
            raise RuntimeError(
                f"factory save obj failed. obj {obj} already been saved with name"
                f" {self._obj2name[obj]}"
            )

    def get_core_objs(self):
        return self._core_objs

    def get_name2clazz(self):
        return self._name2clazz

    def register(self, name, clazz):
        if not isinstance(name, str):
            raise TypeError(
                f"Not supported type {type(name)} for register, expected str"
            )
        if not callable(clazz):
            raise AttributeError(f"register clazz expected callable:{clazz}")
        if name not in self._name2clazz:
            self._name2clazz[name] = clazz
        else:
            raise RuntimeError(
                f"register name '{name}' already been used by class"
                f" {self._name2clazz[name]}"
            )
        if clazz not in self._clazz2name:
            self._clazz2name[clazz] = name
        else:
            raise RuntimeError(
                f"class '{clazz}' already register with name {self._clazz2name[clazz]}"
            )


def register_clazz_as_name(clazz, name):
    factory = Factory()
    factory.register(name, clazz)


def register(obj):
    module_name = inspect.getmodule(obj).__name__
    register_name = f"{module_name}.{obj.__name__}"
    register_clazz_as_name(obj, register_name)
    return obj


def register_module_clazzs(module, top_name):
    for clazz_name in dir(module):
        if not clazz_name.startswith("_"):
            clazz = getattr(module, clazz_name)
            if inspect.isclass(clazz):
                register_clazz_as_name(clazz, f"{top_name}.{clazz_name}")


def register_as(name):
    factory = Factory()

    def inside(clazz):
        factory.register(name, clazz)
        return clazz

    return inside

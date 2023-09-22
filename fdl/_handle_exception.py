import os
import json
from fdl.utils import assert_file_exists, load_json_file_to_dict


def check_key_in_dict(key_str: str, dic: dict):
    key_split = key_str.split(".")
    for key in key_split:
        if key not in dic.keys():
            raise KeyError(
                f"'{key_str}' not exist in config file's dict, which is necessary for fdl."
            )
        dic = dic[key]


def check_value_in_dict_isinstance(key_str, father_clazz, dic, not_empty=False):
    key_split = key_str.split(".")
    for idx, key in enumerate(key_split):
        dic = dic[key]
        if idx == len(key_split) - 1:
            if not isinstance(dic, father_clazz):
                raise TypeError(
                    f"{key_str} in config file expected to be {father_clazz}, got {type(dic)}"
                )
            else:
                if not_empty:
                    if (
                        (isinstance(dic, str) and len(dic.strip()) == 0)
                        or (dic is None)
                        or (isinstance(dic, list) and len(dic) == 0)
                        or (isinstance(dic, dict) and len(dic) == 0)
                    ):
                        raise ValueError(
                            f"'{key_str}' in config file expected not be empty!"
                        )
    return True


def check_objects(objects):
    """检查所有对象都有name和clazz两个属性且不为空且name不重复

    Args:
        objects (_type_): _description_

    Raises:
        RuntimeError: _description_
        TypeError: _description_
        TypeError: _description_
    """
    find_core = False
    element_names = []
    for element in objects:
        if isinstance(element, dict):
            check_key_in_dict("clazz", element)
            check_value_in_dict_isinstance("clazz", str, element, True)
            per_name = element.get("name", None)
            if per_name is not None:
                if per_name in element_names:
                    raise ValueError(f"objects name '{per_name}' have repeats")
                element_names.append(per_name)
        else:
            raise TypeError(
                f"element in config file's objects list expected to be dict, got{type(element)}, element:{element}"
            )


def check_config_file(config_file_path: str):
    """
    TODO:
    config file必须存在，必须能被正确解析，必须符合fdl协议（检查必须项配置），只允许存在一个is_core的对象。且必须存在。

    检查存在字段:
    objects
    检查:
    isinstance(objects, list)

    Args:
        config_file_path (str): _description_
    """
    assert_file_exists(config_file_path)
    config = load_json_file_to_dict(config_file_path)
    # check_key_in_dict("program.name", config) # 不一定需要存在
    # check_key_in_dict("program.saved_path", config) # 不一定需要存在
    check_key_in_dict("objects", config)
    check_value_in_dict_isinstance("objects", list, config, False)
    # check_value_in_dict_isinstance("program.name", str, config, True)
    # check_value_in_dict_isinstance("program.saved_path", str, config)
    check_objects(config["objects"])
    return True

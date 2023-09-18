import os
import shutil
import json


def assert_file_exists(file_path: str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"file {file_path} not found.")


def load_json_file_to_dict(json_file_path):
    with open(json_file_path, "r") as file:
        content = file.read()
    try:
        dic = json.loads(content)
    except json.decoder.JSONDecodeError:
        raise RuntimeError(
            f"{json_file_path} decoder failed. this file's grammar may be wrong."
        )
    return dic


def copy_if_not_exists(file_path: str, dst_dir: str):
    """拷贝file_path到dst_dir，如果dst_dir下没有同名文件的话

    Args:
        file_path (str): 源文件路径
        dst_dir (str): 目标文件夹路径

    Raises:
        FileNotFoundError: _description_
        NotADirectoryError: _description_
        FileExistsError: _description_

    Returns:
        _type_: _description_
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"copy file failed. origin file {file_path} not exists")
    if not os.path.isdir(dst_dir):
        raise NotADirectoryError(f"{dst_dir} is not a Directory")
    file_name = os.path.basename(file_path)
    dst_file_path = os.path.join(dst_dir, file_name)
    if os.path.exists(dst_file_path):
        raise FileExistsError(f"copy file failed. {dst_file_path} already exists.")
    shutil.copyfile(file_path, dst_dir)
    return True


def create_dirs_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        raise FileExistsError(f"create dir failed:'{dir_path}' already exists.")

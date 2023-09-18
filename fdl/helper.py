import os
import re
import sys
from fdl.utils import copy_if_not_exists, create_dirs_if_not_exists
from datetime import datetime


class WorkFolderHelper:
    def __init__(self) -> None:
        self.work_dir = None

    def create(self, saved_path, program_name):
        """创建工作目录，saved_path/program_name/time/"""
        save_abs_path = os.path.abspath(saved_path)

        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        work_dir = os.path.join(save_abs_path, program_name, now)
        create_dirs_if_not_exists(work_dir)
        self.work_dir = work_dir

    def copy_to_work_dir(self, file_path):
        if self.work_dir is not None:
            copy_if_not_exists(file_path, self.work_dir)
        else:
            raise RuntimeError("work_dir not created!")


class BindModuleHelper:
    def __init__(self, module_path) -> None:
        self.module_path = os.path.abspath(module_path)

    def bind(self):
        """
        如果module_path是file，则file直接作为顶层绑定。
        如果module_path是folder，则倒入该folder
        """
        if self.module_path is None:
            return
        if not os.path.exists(self.module_path):
            raise FileNotFoundError(
                f"fdl bind modules error. {self.module_path} not exists!"
            )
        module_path = re.sub("/+$", "", self.module_path)
        dir_path = os.path.dirname(module_path)
        sys.path.append(dir_path)
        module_name = os.path.basename(module_path)
        module_name = re.sub(r"\.py$", "", module_name)
        try:
            exec(f"import {module_name} as _register_module_")
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"fdl bind modules error. This may caused by missing __init__.py file pointer to file in modules. error msg:{e.msg}"
            )
        except ImportError as e:
            raise ImportError(
                f"fdl bind modules error. This may caused by wrong grammar in {module_name}. error msg:{e.msg}"
            )

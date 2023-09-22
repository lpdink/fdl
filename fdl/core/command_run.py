import fdl._handle_exception as exception_handle
from fdl.helper import WorkFolderHelper, BindModuleHelper
from fdl.common import Logger, DictConfig, print_warning
from fdl.factory import Factory
from fdl.utils import copy_if_not_exists


def parse_args(args):
    program_config_path = args.program_config_path
    return program_config_path


def run(args):
    program_config_path = parse_args(args)
    exception_handle.check_config_file(program_config_path)

    # 读取配置文件
    program_config = DictConfig()
    program_config.read(program_config_path)
    # 创建工作区
    work_folder_helper = WorkFolderHelper()
    work_folder_helper.create(
        program_config.program.saved_path, program_config.program.name
    )
    # 创建工作区级log
    logging = Logger()
    logging.set_log_path(work_folder_helper.work_dir)
    # 备份配置文件
    copy_if_not_exists(program_config_path, logging.get_work_dir())
    # 工厂构造对象
    factory = Factory()
    factory.create(program_config)
    # 执行核心对象的func_to_run
    core_objs = factory.get_core_objs()
    if len(core_objs)==0:
        print("No command config in json. Nothing to run. Try set command attr to top objects.")
    for obj in core_objs:
        assert hasattr(obj, "_init_config")
        assert hasattr(obj._init_config, "command")
        func_to_run = obj._init_config.command
        if not hasattr(obj, func_to_run):
            raise AttributeError(
                f"object {obj._init_config.name} don't have method {func_to_run}"
            )
        else:
            func = getattr(obj, func_to_run)
            func()
            # try:
            #     func()
            # except Exception as e:
            #     raise RuntimeError(
            #         f"exec object {obj._init_config.name} core method {func_to_run} failed. error msg : {e}"
            #     )

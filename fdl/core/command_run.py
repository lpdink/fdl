import fdl._handle_exception as exception_handle
from fdl.helper import WorkFolderHelper, BindModuleHelper
from fdl.common import Logger, DictConfig
from fdl.factory import Factory


def parse_args(args):
    program_config_path = args.program_config_path
    func_to_run = args.func_to_run

    return program_config_path, func_to_run


def run(args):
    program_config_path, func_to_run = parse_args(args)
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
    # 工厂构造对象
    factory = Factory()
    factory.create(program_config)
    # 执行核心对象的func_to_run
    core_objs = factory.get_core_objs()
    for obj in core_objs:
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

    # 执行结束
    print("all program done.")

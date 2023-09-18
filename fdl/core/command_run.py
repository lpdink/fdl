import fdl._handle_exception as exception_handle
from fdl.helper import WorkFolderHelper, BindModuleHelper
from fdl.common.log import Logger
from fdl.common.config import DictConfig
from fdl.factory import Factory


def parse_args(args):
    program_config_path = args.program_config_path
    func_to_run = args.func_to_run
    bind_module_path = args.bind

    return program_config_path, func_to_run, bind_module_path


def run(args):
    program_config_path, func_to_run, bind_module_path = parse_args(args)
    exception_handle.check_config_file(program_config_path)
    if bind_module_path is not None:
        bind_helper = BindModuleHelper(bind_module_path)
        bind_helper.bind()
    # 尝试bind临时指定的module

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
            try:
                func()
            except Exception as e:
                raise RuntimeError(
                    f"exec object {obj._init_config.name} core method {func_to_run} failed. error msg : {e}"
                )

    # 执行结束
    print("all program done.")

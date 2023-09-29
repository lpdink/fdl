from fdl._common import Config, Logger
from fdl._factory import Factory
from fdl._utils import check_config_file, copy_if_not_exists, create_workfolder


def is_create_workfolder(project_config: dict):
    if "task" not in project_config.keys():
        return False
    if not isinstance(project_config["task"], dict):
        return False
    if "saved_path" not in project_config["task"].keys():
        return False
    return True


def run(args):
    json_path = args.run_json_path
    check_config_file(json_path)

    project_config = Config()
    project_config.read(json_path)

    logging = Logger()
    # create workspace if set
    if is_create_workfolder(project_config):
        work_dir = create_workfolder(
            project_config["task"]["saved_path"], project_config["task"].get("name", "")
        )
        logging.set_log_path(work_dir)
        # backup json file.
        copy_if_not_exists(json_path, logging.get_work_dir())
    factory = Factory()
    factory.create(project_config)
    # run object with 'method'
    core_objs = factory.get_core_objs()
    if len(core_objs) == 0:
        print(
            "No object with 'method' config in json. Nothing to run. Try set 'method' attr to top objects."
        )
        return
    for obj in core_objs:
        assert hasattr(obj, "_init_config")
        assert hasattr(obj._init_config, "method")
        func_to_run = obj._init_config.method
        if not hasattr(obj, func_to_run):
            raise AttributeError(
                f"object {obj._init_config.name} don't have method {func_to_run}"
            )
        else:
            func = getattr(obj, func_to_run)
            func()

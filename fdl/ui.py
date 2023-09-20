import argparse
import fdl.core as core
from fdl.helper import BindModuleHelper

__VERSION__ = "0.0.1"


def show_version():
    print(f"FDL version : {__VERSION__}")


class TerminalUI:
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()
        self._args = None

    def _add_run(self, sub_parser):
        parser_run = sub_parser.add_parser("run", help="run tasks with json file")
        parser_run.add_argument(
            "func_to_run", type=str, help="function you want to run."
        )
        parser_run.add_argument(
            "program_config_path", type=str, help="config file path of program."
        )
        parser_run.add_argument(
            "-b",
            "--bind",
            type=str,
            nargs="+",
            help="temp bind python file to register modules.",
            required=False,
            default=None,
        )
        parser_run.set_defaults(func=core.run)

    def _add_gen(self, sub_parser):
        parser_gen = sub_parser.add_parser(
            "gen", help="generate json with clazzs, support partly name."
        )
        parser_gen.add_argument(
            "clazzs", nargs="*", help="clazz names you want to gen in a json"
        )
        parser_gen.add_argument(
            "-b",
            "--bind",
            type=str,
            nargs="+",
            help="temp bind python file to register modules.",
            required=False,
            default=None,
        )
        parser_gen.add_argument(
            "-o",
            "--output",
            required=False,
            default="./output.json",
            type=str,
            help="output json file path",
        )
        parser_gen.set_defaults(func=core.gen_json)

    def _add_show(self, sub_parser):
        show_parser = sub_parser.add_parser(
            "show",
            help="show all modules registered, or detail info about some modules.",
        )
        show_parser.add_argument(
            "clazzs",
            nargs="*",
            help="modules you want to show detail info. if not set, show all registered modules' name",
        )
        show_parser.add_argument(
            "-b",
            "--bind",
            type=str,
            nargs="+",
            help="temp bind python file to register modules.",
            required=False,
            default=None,
        )
        show_parser.set_defaults(func=core.show)

    def get_request(self):
        self._parser.add_argument(
            "-v",
            "--version",
            required=False,
            default=False,
            action="store_true",
            help="show fdl version",
        )
        sub_parser = self._parser.add_subparsers()
        # subparser: run
        self._add_run(sub_parser)
        # subparser: gen
        self._add_gen(sub_parser)
        # subparser: show
        self._add_show(sub_parser)

        self._args = self._parser.parse_args()

    def run_request(self):
        if self._args.version:
            show_version()
            return
        # 尝试绑定临时模块
        if getattr(self._args, "bind", None) is not None:
            for bind_path in self._args.bind:
                bind_helper = BindModuleHelper(bind_path)
                bind_helper.bind()
        if hasattr(self._args, "func"):
            import fdl.modules

            self._args.func(self._args)
        else:
            self._parser.print_help()

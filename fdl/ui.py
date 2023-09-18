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

    def show(self):
        pass

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
        # subparser: gen
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
        # TODO: 其他命令,考虑协议与模块的恰当嵌入.
        self._args = self._parser.parse_args()

    def run_request(self):
        if self._args.version:
            show_version()
            return
        # 尝试绑定临时模块
        if self._args.bind is not None:
            for bind_path in self._args.bind:
                bind_helper = BindModuleHelper(bind_path)
                bind_helper.bind()
        if self._args is not None and hasattr(self._args, "func"):
            self._args.func(self._args)
        else:
            raise RuntimeError("run_request failed: request args not set.")

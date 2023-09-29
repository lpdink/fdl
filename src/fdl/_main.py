import argparse
import pathlib

import fdl._core as _core
from fdl._utils import bind

__FDL_VERSION__ = "0.0.1"
__MODULE_PATH__ = (
    pathlib.Path(__file__).parent.joinpath("modules").absolute().as_posix()
)


def show_version():
    print(f"FDL version : {__FDL_VERSION__}")


def get_usage():
    return (
        "\nfdl run Your_Json_Path [-b temp_module]\n"
        "fdl show Partly_Clazz_Name(use '' to show all) [-b Temp_Module]\n"
        "fdl gen [Full_Clazz_Name1, Full_Clazz_Name2...] [-b Temp_Module]\n"
    )


class TerminalParser:
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(
            description=(
                f"Welcome to use FDL {__FDL_VERSION__}. You can copy your module to"
                f" {__MODULE_PATH__} to make the module persistent"
            ),
            usage=get_usage(),
        )
        self.sub_parser = self._parser.add_subparsers()

    def add_arguments(self):
        self._parser.add_argument(
            "-v",
            "--version",
            required=False,
            default=False,
            action="store_true",
            help="show fdl version",
        )
        # subparser: run
        self._add_run()
        # subparser: gen
        self._add_gen()
        # subparser: show
        self._add_show()

    def _add_run(self):
        parser_run = self.sub_parser.add_parser("run", help="run with json file")
        parser_run.add_argument(
            "run_json_path", type=str, help="json path you want to run."
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
        parser_run.set_defaults(func=_core.run)

    def _add_gen(self):
        parser_gen = self.sub_parser.add_parser(
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
        parser_gen.set_defaults(func=_core.gen_json)

    def _add_show(self):
        show_parser = self.sub_parser.add_parser(
            "show",
            help="show all modules registered, or detail info about some modules.",
        )
        show_parser.add_argument(
            "clazz",
            type=str,
            default="",
            help=(
                "module you want to show detail info. if not set, show all registered"
                " modules' name"
            ),
        )
        show_parser.add_argument(
            "-v",
            "--verbose",
            default=False,
            action="store_true",
            help=(
                "module you want to show detail info. if not set, show all registered"
                " modules' name"
            ),
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
        show_parser.set_defaults(func=_core.show)

    def parse_args(self):
        return self._parser.parse_args()

    def print_help(self):
        self._parser.print_help()


def main():
    parser = TerminalParser()
    parser.add_arguments()
    args = parser.parse_args()

    if args.version:
        show_version()
        return
    # try binding temp modules
    if hasattr(args, "bind") and args.bind is not None:
        for bind_path in args.bind:
            bind(bind_path)
    if hasattr(args, "func") and args.func is not None:
        import fdl.modules

        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

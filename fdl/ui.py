import argparse
import fdl.core as core


class TerminalUI:
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()
        self._args = None

    def show(self):
        pass

    def get_request(self):
        sub_parser = self._parser.add_subparsers()
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
            help="temp bind python file to register modules.",
            required=False,
            default=None,
        )
        parser_run.set_defaults(func=core.run)
        self._args = self._parser.parse_args()

    def run_request(self):
        if self._args is not None:
            self._args.func(self._args)
        else:
            raise RuntimeError("run_request failed: request args not set.")

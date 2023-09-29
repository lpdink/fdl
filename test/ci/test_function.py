"""
pytest for function
"""
# pylint:disable=C0114,C0115,C0116
import json
import os
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))
import fdl._core as core  # pylint: disable=C0413
from fdl import register_as
from fdl._factory import Factory


@register_as("Pipeline")
class Pipeline:
    def __init__(self, raw, processors) -> None:
        self.raw = raw
        self.processors = processors
        self.done = False
        self.rst = None

    def process(self):
        for processor in self.processors:
            self.raw = processor.process(self.raw)
        self.done = True
        self.rst = self.raw
        print(self.rst)


@register_as("Converter")
class Converter:
    def __init__(self, src, dst, append=True) -> None:
        self.src = src
        self.dst = dst
        self.append = append

    def process(self, inputs: dict):
        if self.src is not None:
            assert inputs["status"] == self.src

        before = inputs["status"]
        if self.append:
            inputs["status"] += self.dst
        else:
            inputs["status"] = self.dst
        after = inputs["status"]
        inputs["history"].append(f"{before}->{after}")
        return inputs


class Args:
    """simulate as argparser's args"""


class TestFunction:
    def run_with_json_path(self, json_path):
        args = Args()
        setattr(args, "run_json_path", json_path)
        core.run(args)

    def test_mooncake(self):
        factory = Factory()
        self.run_with_json_path("test/ci_resources/jsons/mooncake.json")
        rst = factory._name2obj["MoonCakeFactory"].rst
        assert isinstance(rst, dict)
        assert rst["status"] == "MoonCake"
        assert isinstance(rst["history"], list)
        assert rst["history"] == [
            "raw->raw_flour",
            "raw_flour->raw_flour_milk",
            "raw_flour_milk->raw_flour_milk_salt",
            "raw_flour_milk_salt->mixer",
            "mixer->mixer_egg",
            "mixer_egg->mixer_egg_cool",
            "mixer_egg_cool->mixer_egg_cool_hot",
            "mixer_egg_cool_hot->MoonCake",
        ]

"""
pytest for exception
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
from fdl import register_clazz_as_name


class Args:
    """simulate as argparser's args"""


class TestException:
    """test exception class"""

    def setup_method(self):
        """pytest: will exec begin test_ method."""

    def teardown_method(self):
        """pytest: will exec after test_ method."""

    def run_with_json_path(self, json_path):
        args = Args()
        setattr(args, "run_json_path", json_path)
        core.run(args)

    def test_when_json_not_found(self):
        """test when json not found"""
        with pytest.raises(FileNotFoundError) as excinfo:
            self.run_with_json_path("_not_exists_json_path")
        assert str(excinfo.value) == "file _not_exists_json_path not found."

    def test_when_json_not_valid(self):
        """test when json not valid"""
        invalid_json_path = os.path.join(ROOT, "test/ci_resources/jsons/invalid.json")
        with pytest.raises(json.JSONDecodeError) as excinfo:
            self.run_with_json_path(invalid_json_path)

        assert f"{invalid_json_path} is not a valid json file." in str(excinfo.value)

    def test_when_objects_not_in_dict(self):
        """test when objects not in dict"""
        json_path = os.path.join(
            ROOT, "test/ci_resources/jsons/no_objects_in_dict.json"
        )
        with pytest.raises(KeyError) as excinfo:
            self.run_with_json_path(json_path)
        assert f"{json_path} is a dict, but no 'objects' found." in str(excinfo.value)

    def test_when_objects_not_dict(self):
        """test when objects is not dict"""
        json_path = os.path.join(ROOT, "test/ci_resources/jsons/objects_not_list.json")
        with pytest.raises(TypeError) as excinfo:
            self.run_with_json_path(json_path)
        assert f"objects in {json_path} expected to be list." in str(excinfo.value)

    def test_element_not_dict(self):
        """test when element in objects not dict"""
        json_path = os.path.join(ROOT, "test/ci_resources/jsons/element_not_dict.json")
        with pytest.raises(TypeError) as excinfo:
            self.run_with_json_path(json_path)
        assert "element in 'objects' list expected to be dict, got " in str(
            excinfo.value
        )

    def element_without_clazz(self, json_path):
        """Helper of 'test when element without clazz'"""
        json_path = os.path.join(ROOT, json_path)
        with pytest.raises(KeyError) as excinfo:
            self.run_with_json_path(json_path)
        assert "element in 'objects' list expected to have key 'clazz', got " in str(
            excinfo.value
        )

    def test_element_without_clazz(self):
        """test top type is dict or list"""
        self.element_without_clazz(
            "test/ci_resources/jsons/element_without_clazz_dict.json"
        )
        self.element_without_clazz(
            "test/ci_resources/jsons/element_without_clazz_list.json"
        )

    def test_name_repeat(self):
        """test when element name repeat."""
        json_path = os.path.join(ROOT, "test/ci_resources/jsons/name_repeat.json")
        with pytest.raises(ValueError) as excinfo:
            self.run_with_json_path(json_path)
        assert "top element's name expected not repeat, " in str(excinfo.value)

    def test_clazz_not_register(self):
        """test_clazz_not_register"""
        json_path = os.path.join(
            ROOT, "test/ci_resources/jsons/clazz_not_register.json"
        )
        with pytest.raises(ValueError) as excinfo:
            self.run_with_json_path(json_path)
        assert " not register!" in str(excinfo.value)

    def test_construct_failed(self):
        """test when construct object failed."""
        json_path = os.path.join(
            ROOT, "test/ci_resources/jsons/construct_obj_failed.json"
        )

        def construct_failed():
            raise RuntimeError("construct failed!")

        register_clazz_as_name(construct_failed, "temp_used")
        with pytest.raises(RuntimeError) as excinfo:
            self.run_with_json_path(json_path)
        assert "construct failed!" in str(excinfo.value)

    def test_core_obj_empty(self):
        """test when core obj is empty"""
        json_path = "test/ci_resources/jsons/empty.json"

        class OutputCatcher:
            def __init__(self):
                self.output = ""

            def write(self, msg):
                self.output += msg

            def get_output(self):
                return self.output

        catcher = OutputCatcher()
        sys.stdout = catcher
        self.run_with_json_path(json_path)
        sys.stdout = sys.__stdout__
        assert (
            catcher.get_output()
            == "No object with 'method' config in json. Nothing to run. Try set"
            " 'method'"
            " attr to top objects.\n"
        )

    def test_ref_obj_not_exist(self):
        """test when ref obj not exist"""
        json_path = os.path.join(ROOT, "test/ci_resources/jsons/ref_not_exist.json")

        class Node:
            def __init__(self, uid, children=None) -> None:
                self.uid = uid
                self.children = children

            def print_id(self):
                print(self.uid)
                if isinstance(self.children, list):
                    for child in self.children:
                        child.print_id()

        register_clazz_as_name(Node, "Node")

        with pytest.raises(KeyError) as excinfo:
            self.run_with_json_path(json_path)
        assert "find ref object node2 failed" in str(excinfo.value)

    def test_construct_with_exec_failed(self):
        json_path = os.path.join(
            ROOT, "test/ci_resources/jsons/construct_with_exec.json"
        )

        class Student:
            def __init__(self, name) -> None:
                self.name = name

        register_clazz_as_name(Student, "Student")
        with pytest.raises(RuntimeError) as excinfo:
            self.run_with_json_path(json_path)
        assert "exec sub command" in str(excinfo.value)

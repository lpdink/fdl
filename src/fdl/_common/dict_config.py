# pylint:disable=C0114,C0115,C0116
import json


class Config(dict):
    @classmethod
    def from_dict(cls, **kwargs) -> None:
        config = cls()
        for key, value in kwargs.items():
            if isinstance(value, dict):
                value = Config.from_dict(**value)
            if isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        value[index] = Config.from_dict(**item)
            config[key] = value
        return config

    def read(self, config_path):
        with open(config_path, "r", encoding="utf-8") as file:
            content = file.read()
        data = json.loads(content)
        if isinstance(data, list):
            data = {"objects": data}
        for key, value in data.items():
            if isinstance(value, dict):
                value = Config.from_dict(**value)
            if isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, dict):
                        value[index] = Config.from_dict(**item)
            self[key] = value
        return self

    def get(self, key, default=None):
        if key in self.__dict__:
            return getattr(self, key)
        else:
            return default

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()

    def __iter__(self):
        return iter(self.keys())

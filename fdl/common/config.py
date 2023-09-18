import json


class DictConfig(dict):
    @classmethod
    def from_dict(cls, **kwargs) -> None:
        config = cls()
        for k, v in kwargs.items():
            if isinstance(v, dict):
                v = DictConfig.from_dict(**v)
            if isinstance(v, list):
                for index, item in enumerate(v):
                    if isinstance(item, dict):
                        v[index] = DictConfig.from_dict(**item)
            config[k] = v
        return config

    def read(self, config_path):
        with open(config_path, "r") as file:
            content = file.read()
        data = json.loads(content)
        for k, v in data.items():
            if isinstance(v, dict):
                v = DictConfig.from_dict(**v)
            if isinstance(v, list):
                for index, item in enumerate(v):
                    if isinstance(item, dict):
                        v[index] = DictConfig.from_dict(**item)
            self[k] = v
        return self

    def get(self, key, default=None):
        if key in self.__dict__.keys():
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

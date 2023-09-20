from fdl import register
from functools import partial
from types import FunctionType
try:
    import torchvision.transforms as torchCVT
except ModuleNotFoundError:
    pass
# torchCVT.Normalize()
@register
class TransformBuilder:
    def __init__(self, transforms_args) -> None:
        self.transforms = self._build_transforms(transforms_args)

    def __call__(self, data):
        if not isinstance(data, tuple):
            data = (data,)
        data = list(data)
        for data_trans, data_idx in zip(self.transforms, range(len(data))):
            for trans in data_trans:
                data[data_idx] = trans(data[data_idx])
        return tuple(data)

    def _build_transforms(self, transforms_args):
        all_transforms = []
        for data_trans_args in transforms_args:
            data_transforms = []
            for trans_args in data_trans_args:
                assert 0 < len(trans_args) <= 2
                if len(trans_args) == 2:
                    trans_name, args = trans_args
                else:
                    trans_name = trans_args[0]
                    args = dict()
                clazz = getattr(torchCVT, trans_name, None)
                assert callable(
                    clazz
                ), f"{trans_name} trans function or class not found or callable."
                if isinstance(clazz, FunctionType):  # 函数
                    if len(args) > 0:
                        assert isinstance(
                            args, dict
                        ), f"{trans_name}'s function transform args must be kwargs!"
                        # 利用partial，冻结kwargs，生成新的可调用对象
                        transf = partial(clazz, **args)
                    else:
                        transf = clazz
                elif isinstance(clazz, type):  # 类
                    if isinstance(args, list):
                        # 列表
                        transf = clazz(*args)
                    elif isinstance(args, dict):
                        # 字典
                        transf = clazz(**args)
                    else:
                        raise TypeError(
                            f"unexpected args type: {type(args)} transform:{trans_name}"
                        )
                else:
                    raise TypeError(
                        f"unexpected transform type:{type(clazz)} transform:{trans_name}"
                    )
                data_transforms.append(transf)
            all_transforms.append(data_transforms)
        return all_transforms

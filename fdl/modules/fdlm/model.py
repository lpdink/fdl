from collections import OrderedDict
from fdl import register

torch_exists = True
try:
    import torch
    import torch.nn as nn
    import torch.nn.init as init
except ModuleNotFoundError:
    torch_exists = False


def get_clazz(layer_name):
    # 同名情况，优先级逐渐变高
    clazz = getattr(nn, layer_name, None)
    assert callable(clazz), f"clazz:{clazz} is not callable! layer_name is {layer_name}"
    return clazz


@register
class ConfigModel(nn.Module):
    def __init__(
        self,
        inputs_sizes,
        outputs_sizes,
        layers_args,
    ):
        super().__init__()
        # 为了支持多输入输出，要求input_size和output_size必须是list
        assert isinstance(inputs_sizes, list), "inputs_sizes should be list"
        assert isinstance(outputs_sizes, list), "outputs_sizes should be list"
        assert all(
            isinstance(item, list) for item in inputs_sizes
        ), "item in inputs_sizes should be list"
        assert all(
            isinstance(item, list) for item in outputs_sizes
        ), "item in outputs_sizes should be list"
        self.inputs_sizes = inputs_sizes
        self.outputs_sizes = outputs_sizes
        self.net = self._build_model(layers_args)

    def forward(self, *input_data):
        # # 如果input_data是tensor，包裹它。这使得单个输入和多个输入的处理方式一致
        # if isinstance(input_data, torch.Tensor):
        #     input_data = [input_data]
        # assert isinstance(input_data, list)
        input_data = list(input_data)

        assert len(input_data) == len(self.inputs_sizes)
        # 对多个输入(list)，根据input_size(list)，进行reshape
        for idx in range(len(input_data)):
            # review data shape
            input_data[idx] = input_data[idx].view((-1, *(self.inputs_sizes[idx])))
        if len(input_data) == 1:
            pred = self.net(input_data[0])
        else:
            pred = self.net(input_data)

        # 与input的处理逻辑一致，review多个输出的shape
        if isinstance(pred, torch.Tensor):
            pred = [pred]
        assert isinstance(pred, list)
        assert len(pred) == len(self.outputs_sizes)
        # 对多个输入(list)，根据input_size(list)，进行reshape
        for idx in range(len(pred)):
            # review data shape
            pred[idx] = pred[idx].view((-1, *(self.outputs_sizes[idx])))
        return pred[0] if len(pred) == 1 else pred

    def infer(self, infer_data):
        return self.forward(infer_data)

    def _build_model(self, layers_args: list):
        """根据配置文件中model的layers_args参数构建网络

        Args:
            layers_args (list[list]): dtype=['layer', [layer的构造参数]]
        """
        od = OrderedDict()
        # same_layer_counter用于使得相同类型的层的命名自动+1
        same_layer_counter = dict()
        for layer_args in layers_args:
            assert 0 < len(layer_args) <= 2
            if len(layer_args) == 2:
                layer_name, args = layer_args
            else:
                layer_name = layer_args[0]
                args = []
            clazz = get_clazz(layer_name)
            if layer_name not in same_layer_counter.keys():
                same_layer_counter[layer_name] = 0
            else:
                same_layer_counter[layer_name] += 1
            # dict是Iterable的
            if isinstance(args, list):
                # 列表
                # 考察参数是复杂对象的情况
                arg_objs = []
                for item in args:
                    # 如果item含有key:clazz，则认为是一个对象
                    if isinstance(item, dict) and "clazz" in item.keys():
                        sub_clazz = get_clazz(item["clazz"])
                        sub_args = item.get("args", list())
                        sub_obj = (
                            sub_clazz(*sub_args)
                            if isinstance(sub_args, list)
                            else sub_clazz(**sub_args)
                        )
                        arg_objs.append(sub_obj)
                    elif isinstance(item, list) and all(
                        isinstance(sub_item, dict) and "clazz" in sub_item.keys()
                        for sub_item in item
                    ):
                        sub_arg_objs = []
                        for sub_item in item:
                            sub_clazz = get_clazz(sub_item["clazz"])
                            sub_args = sub_item.get("args", list())
                            sub_obj = (
                                sub_clazz(*sub_args)
                                if isinstance(sub_args, list)
                                else sub_clazz(**sub_args)
                            )
                            sub_arg_objs.append(sub_obj)
                        sub_sub_model = nn.Sequential(*sub_arg_objs)
                        arg_objs.append(sub_sub_model)
                    else:
                        arg_objs.append(item)
                layer = clazz(*arg_objs)
            else:
                # 字典
                layer = clazz(**args)
            od[f"{layer_name}_{same_layer_counter[layer_name]}"] = layer
        return nn.Sequential(od)

    def get_random_input(self, batch_size):
        """返回随机模型输入

        Args:
            batch_size (_type_): _description_

        Returns:
            torch.Tensor: random_input
        """
        # assert len(self.inputs_sizes)==1, "You can only call get_random_input when model has only one input."
        ret = []
        for input_size in self.inputs_sizes:
            if isinstance(input_size, list):
                ret.append(torch.randn((batch_size, *input_size)))
            else:
                ret.append(torch.randn((batch_size, input_size)))
        return ret[0] if len(ret) == 1 else ret

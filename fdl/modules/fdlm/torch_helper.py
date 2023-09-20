from fdl.factory import register_clazz_as_name, register_module_clazzs
from fdl.common import print_warning
import inspect

torch_exists = True
try:
    import torch
    from torch.utils.data.dataloader import DataLoader
except ModuleNotFoundError:
    torch_exists = False

if torch_exists:
    # register
    register_clazz_as_name(DataLoader, "torch.DataLoader")
    # register torch.nn
    register_module_clazzs(torch.nn, "torch.nn")
    # register torch.optim
    register_module_clazzs(torch.optim, "torch.optim")

else:
    print_warning(f"torch not exists. skip register torch modules.")

try:
    import torchvision.datasets
    register_module_clazzs(torchvision.datasets, "torchvision.datasets")
except ModuleNotFoundError:
    pass

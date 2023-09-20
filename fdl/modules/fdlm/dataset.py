from fdl import register
from fdl.common import print_warning
import inspect

torch_exists = True
try:
    import numpy as np
    import torch
except ModuleNotFoundError:
    torch_exists = False


if torch_exists:

    @register
    class SplitDataset(torch.utils.data.Dataset):
        """用于将数据集切分为训练集和测试集，并施加transform，默认访问训练集，可以转换为访问测试集。
        reference from https://github.com/kakaobrain/miro/blob/main/domainbed/datasets/__init__.py#L84 and modified

        """

        def __init__(
            self,
            underlying_dataset,
            train_pct: float = 0.9,
            random: bool = True,
            transform=None,
        ) -> None:
            super().__init__()
            train_dataset_length = int(train_pct * len(underlying_dataset))
            keys = list(range(len(underlying_dataset)))
            if random:
                np.random.shuffle(keys)
            self.keys_train = keys[:train_dataset_length]
            self.keys_test = keys[train_dataset_length:]
            self.underlying_dataset = underlying_dataset
            self.keys = self.keys_train
            self.transform = transform if transform is not None else lambda x: x

        def __getitem__(self, key):
            return self.transform(self.underlying_dataset[self.keys[key]])

        def __len__(self):
            return len(self.keys)

        def convert_to_train(self):
            self.keys = self.keys_train

        def convert_to_test(self):
            self.keys = self.keys_test

else:
    print_warning(f"torch or numpy not exists. skip register torch modules.")

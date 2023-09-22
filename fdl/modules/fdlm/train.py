from fdl import register
from fdl.base import TrainBase
from fdl.common import print_warning

torch_exists = True
try:
    import torch
    from torch.utils.data import DataLoader
except ModuleNotFoundError:
    torch_exists = False


if torch_exists:

    @register
    class Classification(TrainBase):
        def __init__(
            self,
            model: torch.nn.Module,
            loss_f: torch.nn.modules.loss._Loss,
            opt: torch.optim.Optimizer,
            train_dataloader: DataLoader,
            epochs: int = 50,
            device: str = "cuda:0",
            save_epoch_nums: int = 1,
            test_epoch_nums: int = 0,
            seed: int = None,
            continue_train: bool = False,
            compile_model: bool = False,
        ) -> None:
            super().__init__(
                train_dataloader,
                epochs,
                device,
                save_epoch_nums,
                test_epoch_nums,
                seed,
                continue_train,
                compile_model,
            )
            self.model = model
            self.loss_f = loss_f
            self.opt = opt

        def train_step(self, train_data):
            input_data, label = train_data
            pred = self.model(input_data)
            loss = self.loss_f(pred, label)
            point = (pred.argmax(1) == label).sum().item()
            self.opt.zero_grad()
            loss.backward()
            self.opt.step()
            return {
                f"loss": loss.item(),
                f"acc": point / pred.size(0),
            }

else:
    print_warning(f"torch or numpy not exists. skip register torch modules.")

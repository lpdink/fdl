from fdl.common import print_warning

try:
    import torch
    from torch.utils.data import DataLoader
except ModuleNotFoundError:
    print_warning("no module named torch. TrainBase need torch!")

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print_warning("no module named tqdm. TrainBase need tqdm!")

try:
    from torch.utils.tensorboard import SummaryWriter
except ModuleNotFoundError:
    print_warning("no module named tensorboard. TrainBase need tensorboard!")
import os
from fdl.common import Logger
from fdl.utils.torch_utils import convert_devices, load_last_ckpt
from fdl.utils import setup_global_seed
from collections import Counter
from copy import deepcopy


def _write_scale_to_tensorboard(writer, step, *args):
    if writer is not None:
        for name, value in args:
            writer.add_scalar(name, value, step)


class ModelPrepareHelper:
    def __init__(
        self, work_dir, device, compile_model=False, continue_train=False
    ) -> None:
        self.continue_train = continue_train
        self.work_dir = work_dir
        self.compile_model = compile_model
        self.device = device
        self.logging = Logger()

    def get_model_continue_train_path(self, model):
        if hasattr(model, "continue_train"):
            return model.continue_train
        if hasattr(model, "_init_config"):
            if hasattr(model._init_config, "continue_train"):
                return model._init_config.continue_train
        return None

    def load_model_from_path(self, model, model_name, path: str):
        # path is None or path==False
        if not path:
            return model
        if os.path.isfile(path):
            ckpt = torch.load(path, map_location=torch.device("cpu"))
        elif path == "last":
            ckpt, path = load_last_ckpt(self.work_dir, model_name)
        else:
            ckpt = None
        if ckpt is not None:
            self.logging.warning(f"trying load ckpt from {path}")
            model.load_state_dict(ckpt)
        return model

    def preprocess(self, model_obj, model_name):
        if self.compile_model:
            model_obj = torch.compile(model_obj)

        if self.continue_train:
            continue_path = self.get_model_continue_train_path(model_obj)
            model_obj = self.load_model_from_path(model_obj, model_name, continue_path)
        model_obj = model_obj.to(self.device)
        return model_obj


class TrainBase:
    def __init__(
        self,
        train_dataloader: DataLoader,
        epochs: int = 50,
        device: str = "cuda:0",
        save_epoch_nums: int = 1,
        test_epoch_nums: int = 0,
        seed: int = None,
        continue_train: bool = False,
        compile_model: bool = False,
    ) -> None:
        self.train_dataloader = train_dataloader
        self.epochs = epochs
        self.device = convert_devices(device)[0]
        self.seed = seed
        self.save_epoch_nums = int(save_epoch_nums)
        self.test_epoch_nums = int(test_epoch_nums)
        self.logging = Logger()
        self.work_dir = self.logging.get_work_dir()
        self.model_helper = ModelPrepareHelper(
            self.work_dir, self.device, compile_model, continue_train
        )
        self.writer = SummaryWriter(self.work_dir)

    def get_model_names_in_self(self):
        model_names_in_self = [
            attr
            for attr in dir(self)
            if isinstance(getattr(self, attr), torch.nn.Module)
        ]
        return model_names_in_self

    def prepare_models(self):
        model_names = self.get_model_names_in_self()
        for model_name in model_names:
            model = getattr(self, model_name)
            model = self.model_helper.preprocess(model, model_name)
            setattr(self, model_name, model)

    def train(self):
        setup_global_seed(self.seed)
        self.prepare_models()
        self.logging.warning("train epoch begin...")
        self.logging.warning(
            "if you want to see train data(eg. loss), use tensorboard. ckpts and logs also in logdir."
        )
        self.logging.warning(
            f"call tensorboard command:\n tensorboard --logdir {self.work_dir}"
        )
        epoch_tqdm = tqdm(
            range(1, self.epochs + 1),
            colour="blue",
            disable=False,
            desc="epoch",
        )
        step = 0
        for epoch_idx in epoch_tqdm:
            # batch循环
            step = self.train_epoch(epoch_idx, step)
            # 测试
            if self.test_epoch_nums > 0 and epoch_idx % self.test_epoch_nums == 0:
                self.test(epoch_idx)
            # 保存模型
            if self.save_epoch_nums > 0 and (epoch_idx) % self.save_epoch_nums == 0:
                self.save_model(epoch_idx)

    def train_epoch(self, epoch_idx, step):
        train_loader = self.train_dataloader
        batch_tqdm = tqdm(
            train_loader,
            colour="green",
            leave=False,
            disable=False,
            desc="batch",
        )
        sum_ret_dict = None
        for batch_idx, train_data in enumerate(batch_tqdm):
            train_data = [item.to(self.device) for item in train_data]
            step_ret_dict = self.train_step(train_data)
            if sum_ret_dict is None:
                sum_ret_dict = Counter(step_ret_dict)
            else:
                sum_ret_dict += Counter(step_ret_dict)
            _write_scale_to_tensorboard(
                self.writer,
                step,
                *[(name, data) for name, data in step_ret_dict.items()],
            )
            step += 1
        info = f"epoch:{epoch_idx}:" + str(
            {key: value / (batch_idx + 1) for key, value in sum_ret_dict.items()}
        )
        self.logging.debug(info)
        return step

    def train_step(self, train_data):
        raise NotImplementedError(
            "User should implement train_step function by yourself."
        )

    def test(self, epoch_idx):
        self.logging.warning(
            "test function not overwrite, test nothing. consider overwrite TrainBase.test function."
        )

    def save_model(self, epoch_idx):
        model_names = self.get_model_names_in_self()
        for model_name in model_names:
            model = getattr(self, model_name)
            save_path = os.path.join(self.work_dir, f"{model_name}_{epoch_idx}.pt")
            saved_model = deepcopy(model).to("cpu")
            saved_model.eval()
            torch.save(saved_model.state_dict(), save_path)
            self.logging.debug(f"epoch:{epoch_idx} model save at {save_path}")
            del saved_model

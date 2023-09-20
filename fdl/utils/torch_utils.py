import re
import os


def is_cuda_device_available(device):
    import torch

    return torch.cuda.is_available() and device < torch.cuda.device_count()


def convert_devices(devices):
    rst = []
    if isinstance(devices, list):
        if len(devices) == 0:
            raise RuntimeError("devices list expected not empty.")
        for element in devices:
            if isinstance(element, str):
                if element.strip().lower() == "cpu":
                    assert (
                        len(devices) == 1
                    ), "if use cpu, devices should not have other devices."
                    rst.append("cpu")
                    return rst
                if element.strip().lower() == "cuda":
                    assert (
                        len(devices) == 1
                    ), "if devices have cuda, not set idx, devices should not have other devices. if you want use multi-card, set devices like cuda:idx "
                    if not is_cuda_device_available(0):
                        raise RuntimeError(f"devices {element} not available.")
                    rst.append(0)
                    return rst
                pattern = r"(cuda:)?(\d+)"
                match = re.match(pattern, element.strip().lower())
                if match:
                    idx = int(match.group(2))
                    if not is_cuda_device_available(idx):
                        raise RuntimeError(f"devices {element} not available.")
                    else:
                        rst.append(idx)
                else:
                    raise RuntimeError(f"not supported devices type {element}")
            elif isinstance(element, int):
                if not is_cuda_device_available(element):
                    raise RuntimeError(f"devices {element} not available.")
                else:
                    rst.append(element)
            else:
                raise TypeError(
                    f"element in devices expected to be str or int, got {element}"
                )
    elif isinstance(devices, str):
        if devices.strip().lower() == "cpu":
            rst.append("cpu")
            return rst
        if devices.strip().lower() == "cuda":
            if not is_cuda_device_available(0):
                raise RuntimeError(f"devices {devices} not available.")
            rst.append(0)
            return rst
        pattern = r"(cuda:)?(\d+)"
        match = re.match(pattern, devices.strip().lower())
        if match:
            idx = int(match.group(2))
            if not is_cuda_device_available(idx):
                raise RuntimeError(f"devices {devices} not available.")
            else:
                rst.append(idx)
        else:
            raise RuntimeError(f"not supported devices type {devices}")
    elif isinstance(devices, int):
        if not is_cuda_device_available(devices):
            raise RuntimeError(f"devices cuda:{devices} not available.")
        else:
            rst.append(devices)
    else:
        raise TypeError(f"devices expected to be list, str or int, got {devices}")
    if len(rst) != len(set(rst)):
        raise RuntimeError("devices have duplicate item.")
    return rst


def load_last_ckpt(now_work_folder, model_name):
    """从now_work_folder下找到model_name的最后一个ckpt

    Args:
        now_work_folder (_type_): _description_
        model_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    import torch

    task_folder = os.path.dirname(now_work_folder)
    for dir_name in sorted(os.listdir(task_folder), reverse=True):
        last_work_dir = os.path.join(task_folder, dir_name)
        if os.path.isdir(last_work_dir):
            file_names = [
                file_name
                for file_name in os.listdir(last_work_dir)
                if file_name.startswith(model_name) and file_name.endswith(".pt")
            ]

            index_list = [
                int(re.findall(r"(\d+)\.pt", file_name)[0]) for file_name in file_names
            ]

            sorted_files = [
                os.path.join(last_work_dir, file_name)
                for _, file_name in sorted(zip(index_list, file_names), reverse=True)
            ]

            for file in sorted_files:
                try:
                    ckpt = torch.load(file)
                except Exception:
                    continue
                else:
                    return ckpt, file
    return None, None

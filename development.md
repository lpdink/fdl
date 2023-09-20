# FDL软件设计

## 用户感知

```py
fdl run "Key Method Name" config.json [-b temp_bin_module]
fdl genjson clazzA clazzB clazzC [-o output.json]
fdl install modules
fdl uninstall modules
fdl show None/modules/clazz
```

TODO: 优化 fdl show的表现。考虑torch.optim这种对象需要mode.weights的情况，应该如何构造。

## TODO:一篇讨论python frame机制的博客

问题起源于类似如下的代码，解答参考[码农高天的B站视频](https://www.bilibili.com/video/BV1ia411s78e/)
```py
def test():
    obj_name = "not change"
    result = dict()
    exec("obj_name='change'", {"obj_name": obj_name}, result)
    print(obj_name)
    print(result)
```

## TODO:重新抽象factory关于command替换、解析、及执行的封装。

## TODO: 验证目前训练的准确性，mnist的训练不太符合期望，收敛过慢。
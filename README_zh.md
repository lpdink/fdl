# FDL: Fast Dependency Loader

对于算法工程师，您准备在多种数据集，多种模型，不同参数下训练深度学习模型，但是却苦于不断修改代码/资源文件来切换配置？   
对于数据分析师，您编写了不同的数据预处理模块，数据分析策略，可视化模块等等，但是苦于将这些模块连接起来，像流水线那样完成工作？   
更多的情况下，您编写了一些功能性代码片段，但是不易将他们保存下来，往往用一次就弃置，再用时又要重写？  

使用FDL来解决这些问题！  

FDL是纯python编写的，无第三方库依赖的依赖注入框架，语法简洁，易于使用。  
FDL以简单的一个json文件为输入，通过json配置，您可以动态决定程序行为。在模块的支持下，您可以零代码，只简单配置json，快速地完成各种任务。您可以将编写的代码注册为模块，方便地在不同项目之间复用。不同的模块还可以组合起来一起工作。   
您可以从其他人那里取得模块，或者将模块分享出去，黑盒地使用他们。

## 安装 

```sh
pip install fdl
```

## 快速开始

我们创建一个python文件，命名为hello.py，内容如下

```py
from fdl import register_as

@register_as("SayMsgClass")
class SayMsg:
    def __init__(self, msg):
        self.msg = msg

    def say_msg(self):
        print("Hey here! {}".format(self.msg))
```

创建一个json，命名为hello.json，内容如下：

```json
{
    "program": {
        "name": "HelloWorldProject",
        "saved_path": "./fdl_space"
    },
    "objects": [
        {
            "clazz":"SayMsgClass",
            "command":"say_msg",
            "args":{
                "msg":"I am FDL"
            }
        }
    ]
}
```

## 更多示例

## 文档
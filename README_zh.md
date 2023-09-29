# FDL: Fast Dependency Loader

[English](README.md) | 中文

- [FDL: Fast Dependency Loader](#fdl-fast-dependency-loader)
  - [简介](#简介)
  - [安装](#安装)
  - [快速开始](#快速开始)
  - [当构造函数参数是复杂对象](#当构造函数参数是复杂对象)
    - [构造子对象](#构造子对象)
    - [使用引用对象](#使用引用对象)
    - [更复杂的情况](#更复杂的情况)
  - [注册模块的多种方法](#注册模块的多种方法)
    - [register\_as](#register_as)
    - [register](#register)
    - [register\_clazz\_as\_name](#register_clazz_as_name)
  - [自动生成需要的json文件](#自动生成需要的json文件)
  - [持久化您的模块](#持久化您的模块)

## 简介

FDL是纯python编写的，无第三方库依赖的依赖注入框架，语法简洁，易于使用。  
FDL以简单的一个json文件为输入，通过json配置，您可以动态决定程序行为。在模块的支持下，您可以零代码，只简单配置json，快速地完成各种任务。您可以将编写的代码注册为模块，方便地在不同项目之间复用。最赞的是，不同的模块还可以方便地组合起来一起工作。   
您可以从其他人那里取得模块，或者将模块分享出去，黑盒地使用他们。  

## 安装 

```sh
# 推荐python>=3.6
pip install fastDepsLoader
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
        print("Hey here!", self.msg)
```

创建一个json，命名为hello.json，内容如下：

```json
[
    {
        "clazz":"SayMsgClass",
        "method":"say_msg",
        "args":{
            "msg":"I am FDL"
        }
    }
]

```

执行：  

```sh
fdl run hello.json -b hello.py
```

您会看到:

```
Hey here! I am FDL
```

> 发生了什么？  
> -b(--bind)参数指定了fdl临时寻找函数和类定义的python模块（一个python文件或定义了__init__.py的目录）fdl先将hello.py中的SayMsg类注册为名字"SayMsgClass"，这样，我们在json中就可以通过clazz:"SayMsgClass"来构造这个类的对象。  
> args指定了构造对象需要的参数，可以是字典，以关键词参数构造，或者是列表，以位置参数构造。  
> 在所有对象都构造完毕后，如果对象配置了method字段，fdl会按照顺序调用该方法，在本例中，就是say_msg方法。

## 当构造函数参数是复杂对象

json支持的对象只有字典，列表，None，布尔值，整数及浮点数及字符串。当构造函数参数是这些对象时很好配置，可以直接填写。    
但有时候，我们的参数可能是自定义的类或其他复杂对象，如何在json中配置呢？  

fdl提供了两种方法: 使用子对象，或者使用引用对象。

### 构造子对象

我们考虑这样的场景，一个老师在点名，所有的学生要答到。可以实现这样的老师和学生类，保存到teacher.py中：

```py
from fdl import register_as


@register_as("Student")
class Student:
    def __init__(self, name) -> None:
        self.name = name


@register_as("Teacher")
class Teacher:
    def __init__(self, students: list[Student]) -> None:
        self.students = students

    def call_name(self):
        for student in self.students:
            print(student.name)
```

Teacher的构造函数接受一个列表，每个列表元素都是Student对象。json可以如下编写，保存到call.json中：

```json
[
    {
        "clazz": "Teacher",
        "method": "call_name",
        "args": [
            [
                {
                    "clazz": "Student",
                    "args": [
                        "Alice"
                    ]
                },
                {
                    "clazz": "Student",
                    "args": [
                        "Bob"
                    ]
                },
                {
                    "clazz": "Student",
                    "args": [
                        "Candy"
                    ]
                }
            ]
        ]
    }
]
```

执行的命令没有变化：

```
fdl run call.json -b teacher.py
```

这将打印:

```
Alice
Bob
Candy
```

这样的写法很符合直觉，我们在任何地方需要一个复杂对象，只要提供clazz字段（不一定要有args，如果类或函数没有参数，或者都使用默认参数），都能完成构造并注入。

### 使用引用对象

有时候，我们创建的一个子对象希望被多个父对象使用，或者我们不希望子对象又创建子对象，层级太深，容易导致json配置出错。  
此时我们就可以使用引用对象。   
依然是老师点名的场景，这次，我们可以把json如下编写：

```json
[
    {
        "clazz": "Teacher",
        "method": "call_name",
        "args": [
            [
                "${student1}",
                "${student2}",
                "${student3}"
            ]
        ]
    },
    {
        "name": "student1",
        "clazz": "Student",
        "args": [
            "Alice"
        ]
    },
    {
        "name": "student2",
        "clazz": "Student",
        "args": [
            "Bob"
        ]
    },
    {
        "name": "student3",
        "clazz": "Student",
        "args": [
            "Candy"
        ]
    }
]
```

很容易理解，我们为构造的对象添加了name字段，并在父对象中通过${obj_name}的方法来引用它们，这样也能实现与直接构造子对象一样的效果。

> Note:其实是有一些区别的，对于顶层列表，fdl是按照列表的反序构造对象的，而子对象则是按照正序构造的。如果构造对象的顺序对你的程序很关键，你必须了解这个。  
如果让被引用对象(学生)声明在调用对象（老师）之前，会发生什么呢？试试看吧！  
>> (当然，会报错)

### 更复杂的情况

有时候，我们不是直接使用复杂对象，而是使用复杂对象的某个属性或方法的返回值，比如在torch中，我们要构造优化器对象，需要传入model的parameters属性。  
或者，我们需要方便地通过一些代码计算，来得到构造函数的参数，例如，要注入一个随机数。当然这可以通过修改父类代码来完成，但fdl提供了更灵活的方法。   

依然考虑老师点名的场景，现在，我们随机生成一个浮点数作为学生的名字。  

我们可以将学生的名字，例如"Alice"，替换为"@@import random;ret=random.random()@@"，通过@@...@@定界符，我们告诉fdl，这是一条python语句，直接调用解释器去理解这里。   
我们在@@@@中为变量ret赋值，这将作为真正的参数被使用。  
> fdl总是从变量ret中取值，如果调用了@@...@@但是没有为ret赋值，fdl会报错。  
> 你可以通过@@...@@执行任何python代码，不一定要与对象的构造有关，他们都通过调用exec()来执行。  
> exec可以执行任何代码，将代码从json这样的资源文件做注入执行存在一定的风险，因此，请勿执行任何您不信任的json文件！

```json
[
    {
        "clazz": "Teacher",
        "method": "call_name",
        "args": [
            [
                "${student1}",
                "${student2}",
                "${student3}"
            ]
        ]
    },
    {
        "name": "student1",
        "clazz": "Student",
        "args": [
            "@@import random;ret=random.random()@@"
        ]
    },
    {
        "name": "student2",
        "clazz": "Student",
        "args": [
            "@@import random;ret=random.random()@@"
        ]
    },
    {
        "name": "student3",
        "clazz": "Student",
        "args": [
            "@@import random;ret=random.random()@@"
        ]
    }
]
```

这将打印三个随机数，类似于：

```
0.858764185724075
0.19876563235451372
0.42559832725215485
```

## 注册模块的多种方法

容易理解，注册模块使用的名字必须是唯一的，以便您能正确构造模块，否则FDL会产生报错。为不同场景，FDL提供了多种注册模块的方法。

### register_as

正如上一节中演示的那样，register_as接受一个您设置的字符串来调用装饰器，将类或函数（任何有返回值的可调用对象）绑定给该字符串。然后就能在json中使用它来构造对应的对象。    

例如：

```py
from fdl import register_as

@register_as("NodeClazzName")
class Node:
    pass

```

此时您可以使用NodeClazzName来构造对象。

### register

register的对象将由FDL根据对象定义的模块来确定name，例如：

```py
from fdl import register

@register
class Node:
    pass

```

如果它定义在test.py中，您通过-b test.py，尝试创建Node对象，则可以使用名字：test.Node。  
如果它定义在目录test_folder/test_node/test.py下，且您通过__init__.py文件，将Node引入到test_folder模块，尝试-b test_folder，则它会被命名为test_folder.test_node.test.Node。  

您也可以注册库提供的类，例如：

```python
from fdl import register
from torchvision.datasets import MNIST

register(MNIST)
```

MNIST会被注册为：torchvision.datasets.mnist.MNIST

@register在您需要管理大量的模块时很有用，它保证了模块名的唯一性，在您准备[持久化您的模块](#持久化您的模块)时，推荐优先使用它，而不是register_as。

### register_clazz_as_name

与前两个方法不同，register_clazz_as_name不是装饰器，而需要直接调用。适用于您希望为导入的类或函数自行命名时。

例如：

```python
from fdl import register_clazz_as_name
from torchvision.datasets import MNIST

register_clazz_as_name(MNIST, "MNIST_REGISTER_NAME")
```

> 这一方法是语法糖，对于理解装饰器的朋友来说，它实际上等同于：
```python
from fdl import register_as
from torchvision.datasets import MNIST

register = register_as("MNIST_REGISTER_NAME")
register(MNIST)
```

## 自动生成需要的json文件

当我们的项目变得庞大，或者注册的类或函数的数量有很多，有时候，我们不太记得某些类或函数需要哪些参数了，此时我们就可以让fdl来自动生成所需的json文件。   

依然是老师点名的场景，这次，我们让学生的信息丰富起来。修改代码如下：

```python
from fdl import register_as


@register_as("Student")
class Student:
    def __init__(
        self,
        name,
        student_id: int,
        phone: str,
        age: int = 18,
        school_name: str = "Hope Primary School",
        class_number: int = 2,
    ) -> None:
        self.name = name
        self.student_id = student_id
        self.phone = phone
        self.age = age
        self.school_name = school_name
        self.class_number = class_number

    def call_self(self):
        print(
            f"{self.name}, {self.student_id}, {self.phone},"
            f" {self.age},{self.school_name},{self.class_number}"
        )


@register_as("Teacher")
class Teacher:
    def __init__(self, students: list[Student]) -> None:
        self.students = students

    def call_name(self):
        for student in self.students:
            student.call_self()

```

可以看到，除了名字外，我们追加了学号，电话，年龄，学校名，班级编号额外5个字段，并用python注解说明了字段的类型。考虑实际场景，我们假设这些学生大概率有相同的年龄，学校名和班级编号，因此为这几个字段配置了默认值。   
我们更新了老师的call_name方法，以便打印学生的所有信息。  

此时，假设我们需要一名老师来点名，三名学生答到，我们需要生成这样的json文件。  
我们先查看已经注册的所有模块，来看看我们能使用哪些类或函数。  

```sh
fdl show "" -b teacher.py
```

> fdl show的第一个参数接受一个字符串，之后将打印包含该字符串的所有注册的类或函数。这里我们要打印所有的对象和类，故使用""
> 如果添加-v参数，可以看到已经注册的类或函数的文档，和生成json的示例，试试看吧！

这会看到：

```
=============name:clazz=============
Student <class 'teacher.Student'>
Teacher <class 'teacher.Teacher'>
```

我们需要一名老师来点名，三名学生答到，因此我们生成json文件：

```sh
fdl gen Teacher Student Student Student -b doc/gen/teacher.py -o output.json
```

生成的output.json类似于：

```json
{
    "objects": [
        {
            "clazz": "Teacher",
            "def_path": ".../teacher.py",
            "args": {
                "students": "list[teacher.Student]"
            }
        },
        {
            "clazz": "Student",
            "def_path": ".../teacher.py",
            "args": {
                "name": "Todo Here!",
                "student_id": "<class 'int'>",
                "phone": "<class 'str'>",
                "age": 18,
                "school_name": "Hope Primary School",
                "class_number": 2
            }
        },
        {
            "clazz": "Student",
            "def_path": ".../teacher.py",
            "args": {
                "name": "Todo Here!",
                "student_id": "<class 'int'>",
                "phone": "<class 'str'>",
                "age": 18,
                "school_name": "Hope Primary School",
                "class_number": 2
            }
        },
        {
            "clazz": "Student",
            "def_path": ".../teacher.py",
            "args": {
                "name": "Todo Here!",
                "student_id": "<class 'int'>",
                "phone": "<class 'str'>",
                "age": 18,
                "school_name": "Hope Primary School",
                "class_number": 2
            }
        }
    ]
}
```

这与我们之前接触的，最外层是一个列表的情况不同。事实上，最外层是一个列表的情况，是fdl的json配置的简写。您也可以让最外层是一个字典，并在字典的objects字段（需要是一个列表）提供需要构造的对象。就像产生的这个json一样。  

产生的json的对象有def_path字段，记录了函数或类的定义位置，fdl并不使用这个字段，只是为了方便使用者查看类或函数定义。  
可以注意到，对于有默认值的参数，产生的json填写了默认值，没有默认值，但是有类型注解的，产生的json填写了类型注解，如果既没有默认值，又没有类型注解，会填写"Todo Here!"，也需要您手动填写该字段。  
产生的Json并没有method字段，需要手动完成修改，决定调用哪个函数。  


## 持久化您的模块

每次都需要使用-b参数来临时绑定某些模块是令人不快的，如果您充分测试了您的模块，并决定持久地保存它，可以将它拷贝到fdl的模块目录下，以便fdl自动导入它们。   
您可以通过fdl -h来查看模块的位置，您会看到类似于：

```
Welcome to use FDL 0.0.1. You can copy your module to .../fdl/modules to make the module persistent
```

此后，您就可以直接使用这些模块，而无需总是通过-b绑定一系列模块了。  

作者正在考虑设计fdl install和fdl uninstall 命令来帮助您管理模块。
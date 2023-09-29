# FDL: Fast Dependency Loader

English | [中文](https://github.com/lpdink/fdl/blob/main/README_zh.md)

- [FDL: Fast Dependency Loader](#fdl-fast-dependency-loader)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [When Constructor Parameters Are Complex Objects](#when-constructor-parameters-are-complex-objects)
    - [Constructing Child Objects](#constructing-child-objects)
    - [Using Reference Objects](#using-reference-objects)
    - [More Complex Cases](#more-complex-cases)
  - [Registering Modules in Various Ways](#registering-modules-in-various-ways)
    - [register\_as](#register_as)
    - [register](#register)
    - [register\_clazz\_as\_name](#register_clazz_as_name)
  - [Automatically Generate Required JSON Files](#automatically-generate-required-json-files)
  - [Persistent Your Modules](#persistent-your-modules)


## Introduction

FDL is a pure Python-written, dependency injection framework without any third-party library dependencies. Its syntax is simple and easy to use.   
FDL takes a simple JSON file as input, and through JSON configuration, you can dynamically decide the program behavior. With module support, you can quickly complete various tasks with zero code, just by simply configuring JSON. You can register your written code as a module for easy reuse across different projects. The best part is that different modules can be easily combined to work together.   
You can also get modules from others or share your modules, using them like black boxes.

## Installation

```sh
# python>=3.6 is suggested
pip install fastDepsLoader
```

## Quick Start

Create a Python file named hello.py with the following content:

```py
from fdl import register_as

@register_as("SayMsgClass")
class SayMsg:
    def __init__(self, msg):
        self.msg = msg

    def say_msg(self):
        print("Hey here!", self.msg)
```

Create a JSON file named hello.json with the following content:

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

Run:

```sh
fdl run hello.json -b hello.py
```

You will see:

```
Hey here! I am FDL
```

> What happened?   
> 
> The -b (--bind) parameter specifies the Python module (a Python file or a directory with \_\_init\_\_.py) where FDL looks for function and class definitions. FDL first registers the SayMsg class from hello.py with the name "SayMsgClass". This allows us to construct this class's object by specifying clazz:"SayMsgClass" in JSON.   
> 
> args specifies the parameters needed to construct the object, which can be a dictionary for keyword argument construction, or a list for positional argument construction.   
> 
> After all objects are constructed, if an object is configured with the method field, FDL will call this method in order, in this case, the say_msg method.

## When Constructor Parameters Are Complex Objects

JSON only supports dictionaries, lists, None, boolean values, integers, floating-point numbers, and strings. When the constructor parameters are these objects, it's easy to configure. However, sometimes, our parameters could be custom classes or other complex objects. How do we configure them in JSON?  

FDL provides two methods: using child objects or using reference objects.  

### Constructing Child Objects

Consider this scenario: a teacher is calling roll, and all students have to answer. We can implement the teacher and student classes, saving them in teacher.py:

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

The Teacher constructor accepts a list, and each list element is a Student object. JSON can be written as follows, saving it to call.json:

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

Run:

```
fdl run call.json -b teacher.py
```

This will print:

```
Alice
Bob
Candy
```

This writing is very intuitive. We can provide a clazz field (we don't necessarily need args, if the class or function doesn't have parameters, or if all parameters use default values), and we can complete the construction and injection by providing it.

### Using Reference Objects

Sometimes, we create a child object that we want to be used by multiple parent objects, or we don't want the child object to create child objects, and we want to avoid JSON configuration errors. In these cases, we can use reference objects.

Consider the scenario where a teacher is calling roll, and all students have to answer. We can write the JSON as follows:

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

Easily understandable, we add a name field for the constructed objects, and in the parent object, we use the ${obj_name} method to reference them. This achieves the same effect as directly constructing child objects.

> Note: There are some differences. For the top-level list, FDL constructs the objects in reverse order, while child objects are constructed in the forward order. If the order of object construction is critical for your program, you must understand this.   
> If you declare the referenced object (student) before the calling object (teacher), what will happen? Try it and see!  
>> (Of course, it will throw an error)


### More Complex Cases

Sometimes, we don't directly use complex objects, but use the return value of an attribute or method of a complex object. For example, when constructing an optimizer object in torch, we need to pass in the parameters attribute of the model.   
Or, we need to calculate in a convenient way to get the constructor's parameter, such as injecting a random number. Although this can be achieved by modifying the parent class code, FDL provides a more flexible method.

Continuing the scenario where a teacher is calling roll, now we randomly generate a floating-point number as the student's name. We can replace "Alice" with "@@import random;ret=random.random()@@", using the @@...@@ delimiter, we tell FDL that this is a Python statement that can be directly interpreted by the interpreter. We assign the value to ret, which will be used as the actual parameter.

> FDL always takes the value from ret, if you invoke @@...@@ but don't assign a value to ret, FDL will throw an error. 
> You can execute any Python code through @@...@@, not just related to object construction. They are all executed by calling exec().   
> Be careful when executing code from JSON, as it can pose a security risk. Therefore, do not execute any untrusted JSON files!

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

This will print 3 random floats, like:

```
0.858764185724075
0.19876563235451372
0.42559832725215485
```

## Registering Modules in Various Ways

Easily understandable, the name used to register a module must be unique so that you can correctly construct the module, otherwise FDL will produce an error. For different scenarios, FDL provides multiple methods to register modules.

### register_as

As demonstrated in the previous section, register_as accepts a string you set to call the decorator, and binds the class or function (any callable object with a return value) to that string. Then you can use it in JSON to construct the corresponding object. For example:

```py
from fdl import register_as

@register_as("NodeClazzName")
class Node:
    pass

```

In this case, you can use "NodeClazzName" to construct an object.

### register

register function will assign callable object's name by FDL based on the module where the object is defined. 

```py
from fdl import register

@register
class Node:
    pass

```

If it is defined in test.py and you try to create a Node object by -b test.py, you can use the name: test.Node.

If it is defined in the directory test_ folder/test_node/test.py, and you have \_\_init\_\_.py file, importing Node into test_folder module, try -b test_folder, it will be named test_folder.test_node.test.Node.

It is suitable for cases where you need to manage a large number of modules. It ensures the uniqueness of the module name, and it is recommended to use it before [Persistent Your Modules](#persistent-your-modules) instead of register_as.

### register_clazz_as_name

Unlike the previous two methods, register_clazz_as_name is not a decorator but needs to be called directly. It is suitable for cases where you want to name the imported class or function yourself.

```python
from fdl import register_clazz_as_name
from torchvision.datasets import MNIST

register_clazz_as_name(MNIST, "MNIST_REGISTER_NAME")
```

This method is a syntactic sugar, for understanding decorators, it is actually equivalent to:

```python
from fdl import register_as
from torchvision.datasets import MNIST

register = register_as("MNIST_REGISTER_NAME")
register(MNIST)
```

## Automatically Generate Required JSON Files

When your project grows large, or when you have many registered classes or functions, sometimes you forget what parameters a certain class or function needs, and you want FDL to automatically generate the required JSON file for you.

Considering the scenario where a teacher is calling roll, let's make the student's information richer. Modify the code as follows:

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

You can see that, in addition to the name, we added five more fields: student ID, phone number, age, school name, and class number, and used Python annotations to explain the field types. Considering the actual scenario, we assume that these students likely have the same age, school name, and class number, so we configured default values for these fields. We also updated the call_name method of the teacher to print all the student's information.

If we need one teacher to call names, three students to answer, we need to generate the following JSON file:

We first check all registered modules to see which classes or functions we can use.

```sh
fdl show "" -b teacher.py
```

> The first parameter of fdl show accepts a string, and it will print all registered classes or functions that contain that string. Here we want to print all objects and classes, so we use "".   
> If you add the -v parameter, you can see the documentation and example of generating JSON for all registered classes or functions. Try it!

You will see:

```
=============name:clazz=============
Student <class 'teacher.Student'>
Teacher <class 'teacher.Teacher'>
```

This shows that we can use the Student and Teacher classes from the teacher.py module.

The fdl show command is a useful tool for checking the registered classes or functions. It can help you determine which classes or functions you can use when writing JSON configuration files.

Now, if we need one teacher to call names, three students to answer, we need to generate the following JSON file:

```sh
fdl gen Teacher Student Student Student -b doc/gen/teacher.py -o output.json
```

The generated output.json is similar to:

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

This is different from the case where the outer layer is a list. In fact, the outer layer is a list is a shorthand for FDL JSON configuration. You can also make the outer layer a dictionary, and provide a list in the objects field (must be a list) with the objects to be constructed. Just like the generated JSON.

The generated JSON has a def_path field, which records the location of the function or class definition, and FDL does not use this field. It is just for users to view the class or function definition.

For parameters with default values, the generated JSON fills in the default values, and for parameters without default values but with type annotations, the generated JSON fills in the type annotations. If there are no default values and no type annotations, it fills in "Todo Here!", which you need to fill in manually.

The generated JSON does not have a method field, so you need to manually modify it to determine which function to call.

## Persistent Your Modules

Every time you need to use the -b parameter to temporarily bind some modules is not convenient, if you have fully tested your modules and decided to persistently save them, you can copy them to the FDL module directory, so FDL can automatically import them.

You can view the location of the module by running fdl -h. You will see something like:

```
Welcome to use FDL 0.0.1. You can copy your module to .../fdl/modules to make the module persistent
```

Then, you can directly use these modules, without having to bind a series of modules every time.

The author is currently considering designing fdl install and fdl uninstall commands to help you manage modules.
import inspect


class ThirdSrcNode:
    pass


print(inspect.getmodule(ThirdSrcNode))
tmp = inspect.getmodule(ThirdSrcNode)
breakpoint()

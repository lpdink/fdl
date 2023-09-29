# 测试方案

### 异常测试

| 输入数据 | 期望结果 |
|:--------:|:--------:|
|输入文件不存在|error: 文件不存在|
|输入json不合法|error: 输入json不合法|
|输入json是字典格式，但不包含objects对象|error: objects对象不存在|
|objects存在，但本身不是列表类型|error:objects必须是字典类型|
|objects列表元素不是字典类型|error: 元素必须是字典类型|
|输入json是字典格式，顶层objects元素不包含clazz|error: 元素的clazz字段缺失|
|输入json是列表格式，顶层元素不包含clazz|error: 元素的clazz字段缺失|
|列表元素有name字段，但name存在重复|error: 相同的名字被赋予了多个对象|
|配置的clazz没有注册|error: clazz没有注册|
|构造对象失败|error: 对象xxx构造失败，对象配置xxx|
|核心对象列表为空|warning:没有配置了method字段的对象，run nothing|
|引用对象不存在|error:引用对象不存在，构造对象xxx失败，构造配置xxx|
|@@@@exec失败|error:通过语句构造对象失败，尝试执行的语句，error信息|

### 功能测试

| 输入数据 | 期望结果 |
|:--------:|:--------:|
|列表输入构造对象|正常构造且正常调用|
|字典输入构造对象|同上|
|测试基本引用功能|同上|
|测试基本命令构造|同上|
|注册类或函数|通过fdl.getclazz("clazz_name")可以捕获|
|构造基本对象|fdl.create(dict)dict包含字段|
|构造复杂对象|fdl.create(dict)，dict的args字段指向不可序列化对象|
|fdl show xxx|展示包含xxx的所有可调用对象的示例json和__doc__|
|fdl gen|符合期望|
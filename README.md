# Django-Utils

> 通用的Django错误处理流程框架及常用工具函数

## 1. 错误处理

#### ProjectError类

  ```python
from django_utils import ProjectError
  ```

&emsp;&emsp;定义了一个项目中的错误类型及其编号、描述信息、应返回的HTTP状态码等信息。其中描述信息是必需项。 根据项目情况定义适当数量的错误类型，错误类型越多，在测试中就更容易判断具体的错误信息。

```python
class ProjectError(Enum):


    pass
```

#### ProjectException类

> To Be Continued
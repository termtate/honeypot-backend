# 单个蜜罐内的代码说明

## 编写一个新蜜罐
- 可以通过继承`.base.honeypot.Honeypot`的方式创建和配置一个蜜罐，可以参考[real_honeypot.py](/src/feature/real_honeypot.py)的实现和[`Honeypot`的文档](/src/feature/base/honeypot.py#86)，这种方式可以少写代码，但是只能实现固定的功能
  - 如果要添加docker接口，可以参考[conpot.py](conpot.py), [honeyd.py](honeyd.py), [kippo.py](kippo.py), [webtrap.py](webtrap.py)这些蜜罐，多继承一个`DockerMixin`类实现
  - 使用socket通信的蜜罐可以参考[honeyd.py](honeyd.py)
- 可以自己编写相关类实现，具体教程可以看[手动编写类.md](%E6%89%8B%E5%8A%A8%E7%BC%96%E5%86%99%E7%B1%BB.md)。这种方法自由度高，但是写的多
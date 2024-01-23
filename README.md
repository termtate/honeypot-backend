# honeypot-backend

All Async Web App with Fastapi + SQLAlchemy 2.0 + Injector + aioreactive


## before run

- install [rye](https://rye-up.com/guide/installation/)
- install postgresql


## run project

1. `rye sync`（第一次运行项目时输入）
2. `rye run python src/create_tables.py`（创建数据库表）（第一次运行项目时输入）
3. `rye run python src/pre_start.py`（测试数据库连接）
4. `rye run server` 运行服务器
5. http://127.0.0.1:8000/docs 查看openapi文档


## develop
- 建议使用vscode和配套python扩展进行开发
- 运行`rye run lint`格式化代码


## 架构描述

### 项目特点

1. 全部使用协程保证并发性
2. 使用[aioreactive](https://github.com/dbrattli/aioreactive)提供异步流的响应式编程支持
3. 使用[injector](https://github.com/python-injector/injector)提供依赖注入支持
4. fastapi提供对外的网络接口
5. sqlalchemy提供数据库的orm操作
6. rye管理python版本、项目依赖、脚本运行
7. 用ruff和yapf进行代码格式化


### 整体架构

项目从整体上可以划分为3层：
- common层，包含项目最基本的设置和logger模块，供其他所有模块使用
- 用来给实际业务提供功能和整体框架的基础层，基础层实现了主要的框架逻辑，具体的细节需要通过继承子类的方式，由业务层自己实现。基础层包含db, schema和source
- 业务层，用来描述实际接收攻击信息的解析方法、解析之后的数据类、数据库的表以及存储逻辑、fastapi网络接口等功能。
    > 这里的业务具体指处理每一种蜜罐传来的信息、保存这些信息至数据库、进行数据分析、提供网络接口等工作

![整体架构示意图](images/architecture.svg)


业务层中每一个具体业务的大部分功能可以通过继承基础层中的数种Base类来获得，所以基本上对于每一个业务，只需要书写以下代码就能拥有基础功能：
1. 写一个描述蜜罐传来的信息的数据类，并且编写一个方法来把传来的信息转换为这个数据类
2. 写一个sqlalchemy的orm类，来描述用来存储传来信息的数据库的表
  
剩下的代码基本上复制粘贴就可以  
具体的步骤可以看[src/feature/README.md)](/src/feature/README.md)

### 单个蜜罐内的架构

![蜜罐架构示意图](images/honeypot_arch.svg)


> source产生attack的来源也可以不只是socket，只要在内部调用`self.stream.asend()`方法把attack放入stream就可以



## 参考项目

- https://github.com/rhoboro/async-fastapi-sqlalchemy/tree/main Async Web API with FastAPI + SQLAlchemy 2.0
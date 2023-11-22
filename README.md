# honeypot-backend

All Async Web App with Fastapi + SQLAlchemy 2.0 + Injector + aioreactive


## before run

install [rye](https://rye-up.com/guide/installation/)


## run project

1. `rye sync`（第一次运行项目时输入）
2. `rye run test_server` 运行测试（模拟数据）服务器
3. `rye run server` 运行服务器


## develop
- 运行`rye run lint`格式化代码


## 架构描述
1. 全部使用协程保证并发性
2. 使用[aioreactive](https://github.com/dbrattli/aioreactive)提供异步流的响应式编程支持
3. 使用[injector](https://github.com/python-injector/injector)提供依赖注入支持
4. fastapi提供对外的网络接口
5. sqlalchemy提供数据库的orm操作
6. rye管理python版本、项目依赖、脚本运行


### 模块描述



## 参考项目

- https://github.com/rhoboro/async-fastapi-sqlalchemy/tree/main Async Web API with FastAPI + SQLAlchemy 2.0
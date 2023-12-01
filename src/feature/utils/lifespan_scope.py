import asyncio
import threading
from typing import Any, Type, cast
from injector import Provider, Scope, InstanceProvider, Binding
from contextlib import AbstractContextManager, AsyncExitStack, AbstractAsyncContextManager
from typing import TypeVar

T = TypeVar("T", bound=AbstractAsyncContextManager | AbstractContextManager)


class LifespanScope(Scope):
    """
    在该Scope内的类会
    1. 作为单例存在 
    2. 在第一次初始化时会调用__aenter__或__enter__方法
    3. 在fastapi生命周期结束时调用__aexit__或__exit__方法 
    
    (类需要实现`AbstractContextManager`或`AbstractAsyncContextManager`协议)
    """
    stack: AsyncExitStack
    context: dict[Type, Any]

    def configure(self) -> None:
        self.stack = AsyncExitStack()
        self.context = {}
        self._loop = asyncio.new_event_loop()
        self._thr = threading.Thread(
            target=self._loop.run_forever,
            # name="fastapi-injector-enter-context",
            daemon=True,
        )

    def get(self, key: Type[T], provider: Provider[T]) -> Provider[T]:
        """
        仿照injector.singleton和fastapi_injector.request_scope实现
        """
        if key in self.context:
            dep = self.context[key]
        else:
            dep = provider.get(self.injector)
            self.context[key] = dep
            self._register(dep, self.stack)

        return InstanceProvider(dep)

    def _register(self, obj: Any, stack: AsyncExitStack):
        if isinstance(obj, AbstractContextManager):
            stack.enter_context(obj)
        elif isinstance(obj, AbstractAsyncContextManager):
            self._enter_async_context(obj, stack)

    def _enter_async_context(self, obj: Any, stack: AsyncExitStack) -> None:
        # This is the classic "how to call async from sync" problem. See
        # https://stackoverflow.com/a/74710015/260213 for a detailed explanation of how
        # we solve this. In brief, we have a background thread that runs a separate
        # event loop, and the async context is entered on that thread while the calling
        # thread blocks
        try:
            asyncio.get_running_loop()
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            # Starting new event loop
            asyncio.run(stack.enter_async_context(obj))
        else:
            # Event loop is running, enter the context on a background thread
            self._run_async(stack.enter_async_context(obj))

    def _run_async(self, coroutine):
        # This will block the calling thread until the coroutine is finished.
        # Any exception that occurs in the coroutine is raised in the caller
        if not self._thr.is_alive():
            self._thr.start()
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        return future.result()

    async def aclose(self):
        await self.stack.aclose()


def lifespan_scope(cls: Type[T]) -> Type[T]:
    """
    LifespanScope的类装饰器
    """
    cast(Any, cls).__scope__ = LifespanScope
    if binding := getattr(cls, "__binding__", None):
        new_binding = Binding(
            interface=binding.interface,
            provider=binding.provider,
            scope=LifespanScope
        )
        setattr(cls, "__binding__", new_binding)

    return cls

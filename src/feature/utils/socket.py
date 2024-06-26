import asyncio

from schema import Socket
from typing import (
    Callable,
    Awaitable,
    Any,
    Type,
    TypeVar,
    ParamSpec,
)
from expression import curry

T = TypeVar("T")
TException = TypeVar("TException", bound=Exception)
P = ParamSpec("P")


@curry(2)
def catch(
    error: Type[TException],
    block: Callable[P, Awaitable[T]],
    on_exception: Callable[[TException], Any],
) -> Callable[P, Awaitable[T | None]]:
    async def inner(*args: P.args, **kwargs: P.kwargs):
        try:
            return await block(*args, **kwargs)
        except error as e:
            on_exception(e)

    return inner


async def start_server(
    socket: Socket,
    on_receive: Callable[[bytes], Awaitable],
):
    # https://docs.python.org/zh-cn/3.10/library/asyncio-stream.html#tcp-echo-server-using-streams
    async def handle_data(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        data = await reader.read()

        await on_receive(data)

        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handle_data, socket.ip, socket.port)

    async with server:
        await server.serve_forever()


# TS = TypeVar("TS", bound=ModelBase)


# class SocketSource(DataSource[TS], Protocol[TS]):
#     """
#     对来源是socket发送数据的DataSource的封装

#     用法：

#     >>> @lifespan_scope
#     >>> @inject_constructor
#     >>> class MySource(SocketSource[MyDBModel]):
#     >>>     schema = MySchema
#     >>>     socket = Socket(ip=..., port=...)
#     >>>     logger: Logger
#     >>>     crud: CRUDWithSession[MyDBModel]
#     """

#     socket: ClassVar[Socket]
#     logger: Logger

#     async def receive_data_forever(self):
#         self.logger.info(f"start listening socket on {self.socket}")

#         async def validate_and_store(s: str | bytes):
#             a = await self.add(s)
#             await self.crud.create(a)

#         return await start_server(
#             socket=self.socket,
#             on_receive=catch(ValidationError)(validate_and_store)(
#                 on_exception=lambda e: self.logger.warning(
#                     f"validate error: {e.json(indent=2, include_url=False)}"
#                 )
#             ),
#         )

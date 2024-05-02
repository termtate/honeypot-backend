from typing import Callable, Type, TypeVar, Generic, cast, TYPE_CHECKING
from feature.main import source, MainAttackModel
from aioreactive import AsyncSubject, AsyncAnonymousObserver
from source import DataSource
from db.models import ModelBase
from ..lifespan_context import LifespanContext

if TYPE_CHECKING:
    from ..honeypot import Honeypot


TDBModel = TypeVar("TDBModel", bound=ModelBase, contravariant=True)


class MainStream(LifespanContext, Generic[TDBModel]):
    def __init__(
        self, transform: Callable[[TDBModel], MainAttackModel]
    ) -> None:
        self.transform = transform
        self.lifespan_events = set()

    async def configure(self, honeypot: Type["Honeypot"]):
        stream: AsyncSubject[MainAttackModel] = source.stream
        hs = cast(
            DataSource[TDBModel],
            honeypot.source,  # type: ignore
        )

        async def sus(a):
            await stream.asend(self.transform(a))

        self.lifespan_events.add(
            await hs.stream.subscribe_async(AsyncAnonymousObserver(asend=sus))
        )

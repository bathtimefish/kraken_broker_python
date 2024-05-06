from abc import ABCMeta, abstractmethod

class Broker(metaclass=ABCMeta):
    @abstractmethod
    async def on(self, kind: str, provider: str, payload: str) -> None:
        pass
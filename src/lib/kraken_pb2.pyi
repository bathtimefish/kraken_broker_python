from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class KrakenMessageRequest(_message.Message):
    __slots__ = ("kind", "provider", "payload")
    KIND_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    kind: str
    provider: str
    payload: str
    def __init__(self, kind: _Optional[str] = ..., provider: _Optional[str] = ..., payload: _Optional[str] = ...) -> None: ...

class KrakenMessageResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: int
    def __init__(self, status: _Optional[int] = ...) -> None: ...

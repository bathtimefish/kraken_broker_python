from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class KrakenRequest(_message.Message):
    __slots__ = ["collector_name", "content_type", "metadata", "payload"]
    COLLECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    collector_name: str
    content_type: str
    metadata: str
    payload: bytes
    def __init__(self, collector_name: _Optional[str] = ..., content_type: _Optional[str] = ..., metadata: _Optional[str] = ..., payload: _Optional[bytes] = ...) -> None: ...

class KrakenResponse(_message.Message):
    __slots__ = ["collector_name", "content_type", "metadata", "payload"]
    COLLECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    collector_name: str
    content_type: str
    metadata: str
    payload: bytes
    def __init__(self, collector_name: _Optional[str] = ..., content_type: _Optional[str] = ..., metadata: _Optional[str] = ..., payload: _Optional[bytes] = ...) -> None: ...

from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShapeType(_message.Message):
    __slots__ = ("shape_type",)
    SHAPE_TYPE_FIELD_NUMBER: _ClassVar[int]
    shape_type: str
    def __init__(self, shape_type: _Optional[str] = ...) -> None: ...

class ShapeId(_message.Message):
    __slots__ = ("shape_id",)
    SHAPE_ID_FIELD_NUMBER: _ClassVar[int]
    shape_id: str
    def __init__(self, shape_id: _Optional[str] = ...) -> None: ...

class Shape(_message.Message):
    __slots__ = ("shape_id", "shape_type", "coords")
    SHAPE_ID_FIELD_NUMBER: _ClassVar[int]
    SHAPE_TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDS_FIELD_NUMBER: _ClassVar[int]
    shape_id: str
    shape_type: str
    coords: _containers.RepeatedCompositeFieldContainer[ShapeCoord]
    def __init__(self, shape_id: _Optional[str] = ..., shape_type: _Optional[str] = ..., coords: _Optional[_Iterable[_Union[ShapeCoord, _Mapping]]] = ...) -> None: ...

class ShapeCoord(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Code(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[Code]
    INVALID_SHAPE: _ClassVar[Code]
    INVALID_PERIMETER: _ClassVar[Code]
    INVALID_SHAPE_ID: _ClassVar[Code]
    SHAPE_NOT_FOUND: _ClassVar[Code]
    AREA_NOT_FOUND: _ClassVar[Code]
OK: Code
INVALID_SHAPE: Code
INVALID_PERIMETER: Code
INVALID_SHAPE_ID: Code
SHAPE_NOT_FOUND: Code
AREA_NOT_FOUND: Code

class CreateShapeResponse(_message.Message):
    __slots__ = ("status_code", "message", "shape")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    status_code: Code
    message: str
    shape: Shape
    def __init__(self, status_code: _Optional[_Union[Code, str]] = ..., message: _Optional[str] = ..., shape: _Optional[_Union[Shape, _Mapping]] = ...) -> None: ...

class GetShapeResponse(_message.Message):
    __slots__ = ("status_code", "message", "shape")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    status_code: Code
    message: str
    shape: Shape
    def __init__(self, status_code: _Optional[_Union[Code, str]] = ..., message: _Optional[str] = ..., shape: _Optional[_Union[Shape, _Mapping]] = ...) -> None: ...

class GetPerimetersGreaterThanResponse(_message.Message):
    __slots__ = ("status_code", "message", "perimeter", "shape")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PERIMETER_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    status_code: Code
    message: str
    perimeter: float
    shape: Shape
    def __init__(self, status_code: _Optional[_Union[Code, str]] = ..., message: _Optional[str] = ..., perimeter: _Optional[float] = ..., shape: _Optional[_Union[Shape, _Mapping]] = ...) -> None: ...

class GetTotalAreaResponse(_message.Message):
    __slots__ = ("status_code", "message", "total_area", "valid_ids", "invalid_ids")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_AREA_FIELD_NUMBER: _ClassVar[int]
    VALID_IDS_FIELD_NUMBER: _ClassVar[int]
    INVALID_IDS_FIELD_NUMBER: _ClassVar[int]
    status_code: Code
    message: str
    total_area: float
    valid_ids: _containers.RepeatedCompositeFieldContainer[ShapeId]
    invalid_ids: _containers.RepeatedCompositeFieldContainer[ShapeId]
    def __init__(self, status_code: _Optional[_Union[Code, str]] = ..., message: _Optional[str] = ..., total_area: _Optional[float] = ..., valid_ids: _Optional[_Iterable[_Union[ShapeId, _Mapping]]] = ..., invalid_ids: _Optional[_Iterable[_Union[ShapeId, _Mapping]]] = ...) -> None: ...

class GetAreasResponse(_message.Message):
    __slots__ = ("status_code", "message", "area", "shape")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    AREA_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    status_code: Code
    message: str
    area: float
    shape: Shape
    def __init__(self, status_code: _Optional[_Union[Code, str]] = ..., message: _Optional[str] = ..., area: _Optional[float] = ..., shape: _Optional[_Union[Shape, _Mapping]] = ...) -> None: ...

class MinPerimeter(_message.Message):
    __slots__ = ("min_perimeter",)
    MIN_PERIMETER_FIELD_NUMBER: _ClassVar[int]
    min_perimeter: float
    def __init__(self, min_perimeter: _Optional[float] = ...) -> None: ...

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

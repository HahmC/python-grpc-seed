# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: grpc_server.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'grpc_server.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11grpc_server.proto\"\x1f\n\tShapeType\x12\x12\n\nshape_type\x18\x01 \x01(\t\"\x1b\n\x07ShapeId\x12\x10\n\x08shape_id\x18\x01 \x01(\x05\"J\n\x05Shape\x12\x10\n\x08shape_id\x18\x01 \x01(\x05\x12\x12\n\nshape_type\x18\x02 \x01(\t\x12\x1b\n\x06\x63oords\x18\x03 \x03(\x0b\x32\x0b.ShapeCoord\"\"\n\nShapeCoord\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\x32Q\n\nGrpcServer\x12#\n\x0b\x43reateShape\x12\n.ShapeType\x1a\x06.Shape\"\x00\x12\x1e\n\x08GetShape\x12\x08.ShapeId\x1a\x06.Shape\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'grpc_server_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SHAPETYPE']._serialized_start=21
  _globals['_SHAPETYPE']._serialized_end=52
  _globals['_SHAPEID']._serialized_start=54
  _globals['_SHAPEID']._serialized_end=81
  _globals['_SHAPE']._serialized_start=83
  _globals['_SHAPE']._serialized_end=157
  _globals['_SHAPECOORD']._serialized_start=159
  _globals['_SHAPECOORD']._serialized_end=193
  _globals['_GRPCSERVER']._serialized_start=195
  _globals['_GRPCSERVER']._serialized_end=276
# @@protoc_insertion_point(module_scope)

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: kraken.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ckraken.proto\x12\x06kraken\"`\n\rKrakenRequest\x12\x16\n\x0e\x63ollector_name\x18\x01 \x01(\t\x12\x14\n\x0c\x63ontent_type\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t\x12\x0f\n\x07payload\x18\x04 \x01(\x0c\"a\n\x0eKrakenResponse\x12\x16\n\x0e\x63ollector_name\x18\x01 \x01(\t\x12\x14\n\x0c\x63ontent_type\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t\x12\x0f\n\x07payload\x18\x04 \x01(\x0c\x32V\n\rKrakenService\x12\x45\n\x14ProcessKrakenRequest\x12\x15.kraken.KrakenRequest\x1a\x16.kraken.KrakenResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'kraken_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_KRAKENREQUEST']._serialized_start=24
  _globals['_KRAKENREQUEST']._serialized_end=120
  _globals['_KRAKENRESPONSE']._serialized_start=122
  _globals['_KRAKENRESPONSE']._serialized_end=219
  _globals['_KRAKENSERVICE']._serialized_start=221
  _globals['_KRAKENSERVICE']._serialized_end=307
# @@protoc_insertion_point(module_scope)

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: osi3/osi_trafficcommandupdate.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from osi3 import osi_version_pb2 as osi3_dot_osi__version__pb2
from osi3 import osi_common_pb2 as osi3_dot_osi__common__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n#osi3/osi_trafficcommandupdate.proto\x12\x04osi3\x1a\x16osi3/osi_version.proto\x1a\x15osi3/osi_common.proto\"\xb5\x02\n\x14TrafficCommandUpdate\x12\'\n\x07version\x18\x01 \x01(\x0b\x32\x16.osi3.InterfaceVersion\x12\"\n\ttimestamp\x18\x02 \x01(\x0b\x32\x0f.osi3.Timestamp\x12\x30\n\x16traffic_participant_id\x18\x03 \x01(\x0b\x32\x10.osi3.Identifier\x12\x44\n\x10\x64ismissed_action\x18\x04 \x03(\x0b\x32*.osi3.TrafficCommandUpdate.DismissedAction\x1aX\n\x0f\x44ismissedAction\x12-\n\x13\x64ismissed_action_id\x18\x01 \x01(\x0b\x32\x10.osi3.Identifier\x12\x16\n\x0e\x66\x61ilure_reason\x18\x02 \x01(\tB\x02H\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'osi3.osi_trafficcommandupdate_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'H\001'
  _TRAFFICCOMMANDUPDATE._serialized_start=93
  _TRAFFICCOMMANDUPDATE._serialized_end=402
  _TRAFFICCOMMANDUPDATE_DISMISSEDACTION._serialized_start=314
  _TRAFFICCOMMANDUPDATE_DISMISSEDACTION._serialized_end=402
# @@protoc_insertion_point(module_scope)

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\"\t\n\x07NoParam\"-\n\x07\x41\x63\x63ount\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"\x1d\n\x08\x41\x63\x63ounts\x12\x11\n\tusernames\x18\x01 \x01(\t\"0\n\x0eServerResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\r\n\x05\x65rror\x18\x02 \x01(\x08\"@\n\x0bMessageInfo\x12\x13\n\x0b\x64\x65stination\x18\x01 \x01(\t\x12\x0e\n\x06source\x18\x02 \x01(\t\x12\x0c\n\x04text\x18\x03 \x01(\t\" \n\nSearchTerm\x12\x12\n\nsearchterm\x18\x01 \x01(\t2\xda\x02\n\x04\x43hat\x12,\n\rCreateAccount\x12\x08.Account\x1a\x0f.ServerResponse\"\x00\x12,\n\rDeleteAccount\x12\x08.Account\x1a\x0f.ServerResponse\"\x00\x12$\n\x05Login\x12\x08.Account\x1a\x0f.ServerResponse\"\x00\x12%\n\x06Logout\x12\x08.Account\x1a\x0f.ServerResponse\"\x00\x12(\n\x0cListAccounts\x12\x0b.SearchTerm\x1a\t.Accounts\"\x00\x12.\n\x0bSendMessage\x12\x0c.MessageInfo\x1a\x0f.ServerResponse\"\x00\x12,\n\x0eListenMessages\x12\x08.Account\x1a\x0c.MessageInfo\"\x00\x30\x01\x12!\n\tHeartbeat\x12\x08.NoParam\x1a\x08.NoParam\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _NOPARAM._serialized_start=14
  _NOPARAM._serialized_end=23
  _ACCOUNT._serialized_start=25
  _ACCOUNT._serialized_end=70
  _ACCOUNTS._serialized_start=72
  _ACCOUNTS._serialized_end=101
  _SERVERRESPONSE._serialized_start=103
  _SERVERRESPONSE._serialized_end=151
  _MESSAGEINFO._serialized_start=153
  _MESSAGEINFO._serialized_end=217
  _SEARCHTERM._serialized_start=219
  _SEARCHTERM._serialized_end=251
  _CHAT._serialized_start=254
  _CHAT._serialized_end=600
# @@protoc_insertion_point(module_scope)

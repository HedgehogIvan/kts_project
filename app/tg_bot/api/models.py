from dataclasses import field
from typing import ClassVar, Type, List, Optional

from marshmallow_dataclass import dataclass
from marshmallow import Schema, EXCLUDE, INCLUDE


@dataclass
class MessageFrom:
    id: int
    first_name: str
    last_name: Optional[str]
    username: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class User:
    id: int
    first_name: str
    last_name: Optional[str]
    username: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class ChatMember:
    status: str
    user: User

    class Meta:
        unknown = EXCLUDE


@dataclass
class ChatMemberUpdated:
    chat: Chat
    from_: MessageFrom
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    from_: Optional[MessageFrom] = field(metadata={"data_key": "from"})
    sender_chat: Optional[Chat]
    chat_member: Optional[ChatMemberUpdated]
    chat: Chat
    text: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


# @dataclass
# class GetUpdatesResponse:
#     ok: bool
#     result: List[UpdateObj]
#
#     Schema: ClassVar[Type[Schema]] = Schema
#
#     class Meta:
#         unknown = EXCLUDE


@dataclass
class MessageUpdateObj(UpdateObj):
    message: Message


@dataclass
class ChannelPostUpdateObj(UpdateObj):
    channel_post: Message


@dataclass
class ChatMemberUpdateObj(UpdateObj):
    chat_member: ChatMemberUpdated


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE

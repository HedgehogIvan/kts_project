from dataclasses import field, dataclass
from typing import ClassVar, Type, List, Optional

from marshmallow_dataclass import dataclass as mm_dataclass
from marshmallow import Schema, EXCLUDE, INCLUDE


@mm_dataclass
class MessageFrom:
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class User:
    id: int
    first_name: str
    last_name: Optional[str]
    username: str

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class ChatMember:
    status: str
    user: User

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class ChatMemberUpdated:
    chat: Chat
    from_: MessageFrom
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class Message:
    message_id: int
    from_: Optional[MessageFrom] = field(metadata={"data_key": "from"})
    sender_chat: Optional[Chat]
    chat_member: Optional[ChatMemberUpdated]
    chat: Chat
    text: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class CallbackQuery:
    query_id: int = field(metadata={"data_key": "id"})
    from_: MessageFrom = field(metadata={"data_key": "from"})
    message: Optional[Message]
    data: Optional[str]

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class UpdateObj:
    update_id: int

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@mm_dataclass
class MessageUpdateObj(UpdateObj):
    message: Message


@mm_dataclass
class ChannelPostUpdateObj(UpdateObj):
    channel_post: Message


@mm_dataclass
class ChatMemberUpdateObj(UpdateObj):
    chat_member: ChatMemberUpdated


@mm_dataclass
class CallbackQueryObj(UpdateObj):
    callback_query: CallbackQuery


@mm_dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class AnswerForCallbackQuery:
    callback_query_id: str
    text: Optional[str]
    show_alert: Optional[bool]


@dataclass
class InlineButton:
    text: str
    callback_data: Optional[str] = None


@dataclass
class InlineKeyboard:
    inline_keyboard: list = field(default=list[InlineButton])


@dataclass
class KeyboardButton:
    text: str


@dataclass
class ReplyKeyboard:
    keyboard: list = field(default=list[InlineButton])
    resize_keyboard: bool = False
    one_time_keyboard: bool = False
    selective: bool = False


@dataclass
class ReplyKeyboardRemove:
    remove_keyboard: bool = True
    selective: bool = False


@dataclass
class MessageToSend:
    chat_id: int
    text: str
    reply_markup: InlineKeyboard | ReplyKeyboard | ReplyKeyboardRemove | None = None


@dataclass
class UpdateMessage:
    chat_id: int
    message_id: int
    text: str
    reply_markup: Optional[InlineKeyboard] = None

from typing import Any

from pydantic import BaseModel, Field


class Account(BaseModel):
    id: int = Field(..., example=7)
    name: str = Field(..., example="Vilaink")


class AdditionalAttributes(BaseModel):
    username: str | None = Field(None, example="aurelius66")
    language_code: str | None = Field(None, example="ru")
    social_telegram_user_id: int | None = Field(None, example=759259958)
    social_telegram_user_name: str | None = Field(None, example="aurelius66")


class Sender(BaseModel):
    id: int = Field(..., example=1621)
    name: str = Field(..., example="Аврелий ")
    email: str | None = Field(None, example=None)
    identifier: str | None = Field(None, example=None)
    phone_number: str | None = Field(None, example=None)
    avatar: str = Field("", example="")
    thumbnail: str = Field("", example="")
    additional_attributes: AdditionalAttributes = Field(
        default_factory=AdditionalAttributes
    )
    custom_attributes: dict[str, Any] = Field(default_factory=dict)


class ContactInbox(BaseModel):
    id: int = Field(..., example=1648)
    contact_id: int = Field(..., example=1621)
    inbox_id: int = Field(..., example=86)
    source_id: str = Field(..., example="759259958")
    created_at: str = Field(..., example="2025-07-01T14:22:46.783Z")
    updated_at: str = Field(..., example="2025-07-01T14:22:46.783Z")
    hmac_verified: bool = Field(..., example=False)
    pubsub_token: str = Field(..., example="iWiCCmHnHTLVHuyqnTGykBAP")


class MessageSenderAdditionalAttributes(BaseModel):
    username: str | None = Field(None, example="aurelius66")
    language_code: str | None = Field(None, example="ru")
    social_telegram_user_id: int | None = Field(None, example=759259958)
    social_telegram_user_name: str | None = Field(None, example="aurelius66")


class MessageSender(BaseModel):
    id: int = Field(..., example=1621)
    name: str = Field(..., example="Аврелий ")
    email: str | None = Field(None)
    identifier: str | None = Field(None)
    phone_number: str | None = Field(None)
    avatar: str = Field("", example="")
    thumbnail: str = Field("", example="")
    additional_attributes: MessageSenderAdditionalAttributes = Field(
        default_factory=MessageSenderAdditionalAttributes
    )
    custom_attributes: dict[str, Any] = Field(default_factory=dict)
    type: str | None = Field(None, example="contact")


class MessageConversationMetaContactInbox(BaseModel):
    source_id: str = Field(..., example="759259958")


class MessageConversationMetaReferralSource(BaseModel):
    # Add fields if available or keep empty dict for now
    pass


class MessageConversationMeta(BaseModel):
    sender: MessageSender = Field(...)
    assignee: Any | None = Field(None)
    team: Any | None = Field(None)
    hmac_verified: bool = Field(..., example=False)


class MessageConversation(BaseModel):
    assignee_id: Any | None = Field(None)
    unread_count: int = Field(..., example=1)
    last_activity_at: int = Field(..., example=1751379766)
    contact_inbox: MessageConversationMetaContactInbox = Field(...)
    referral_source: MessageConversationMetaReferralSource = Field(
        default_factory=MessageConversationMetaReferralSource
    )


class Message(BaseModel):
    id: int = Field(..., example=9048)
    content: str = Field(..., example="/start")
    account_id: int = Field(..., example=7)
    inbox_id: int = Field(..., example=86)
    conversation_id: int = Field(..., example=439)
    message_type: int = Field(..., example=0)
    created_at: int = Field(..., example=1751379766)
    updated_at: str = Field(..., example="2025-07-01T14:22:46.891Z")
    private: bool = Field(..., example=False)
    status: str = Field(..., example="sent")
    source_id: str | None = Field(None, example="134")
    content_type: str = Field(..., example="text")
    content_attributes: dict[str, Any] = Field(default_factory=dict)
    sender_type: str = Field(..., example="Contact")
    sender_id: int = Field(..., example=1621)
    external_source_ids: dict[str, Any] = Field(default_factory=dict)
    additional_attributes: dict[str, Any] = Field(default_factory=dict)
    processed_message_content: str = Field(..., example="/start")
    sentiment: dict[str, Any] = Field(default_factory=dict)
    source_type_id: Any | None = Field(None)
    conversation: MessageConversation = Field(...)
    sender: MessageSender = Field(...)


class Conversation(BaseModel):
    additional_attributes: dict[str, Any] = Field(default_factory=dict)
    can_reply: bool = Field(..., example=True)
    channel: str = Field(..., example="Channel::Telegram")
    contact_inbox: ContactInbox = Field(...)
    id: int = Field(..., example=439)
    inbox_id: int = Field(..., example=86)
    messages: list[Message] = Field(...)
    labels: list[Any] = Field(default_factory=list)
    meta: dict[str, Any] = Field(...)  # or create a model if needed
    status: str = Field(..., example="pending")
    custom_attributes: dict[str, Any] = Field(default_factory=dict)
    snoozed_until: Any | None = Field(None)
    unread_count: int = Field(..., example=1)
    first_reply_created_at: Any | None = Field(None)
    priority: Any | None = Field(None)
    waiting_since: int = Field(..., example=1751379766)
    agent_last_seen_at: int = Field(..., example=0)
    contact_last_seen_at: int = Field(..., example=0)
    last_activity_at: int = Field(..., example=1751379766)
    timestamp: int = Field(..., example=1751379766)
    created_at: int = Field(..., example=1751379766)
    applied_sla: Any | None = Field(None)
    sla_events: list[Any] = Field(default_factory=list)
    sla_policy_id: Any | None = Field(None)


class Inbox(BaseModel):
    id: int = Field(..., example=86)
    name: str = Field(..., example="sola_ai_bot")


class VialinkWebhookPayload(BaseModel):
    account: Account = Field(...)
    additional_attributes: dict[str, Any] = Field(default_factory=dict)
    content_attributes: dict[str, Any] = Field(default_factory=dict)
    content_type: str = Field(..., example="text")
    content: str = Field(..., example="/start")
    conversation: Conversation = Field(...)
    created_at: str = Field(..., example="2025-07-01T14:22:46.891Z")
    id: int = Field(..., example=9048)
    inbox: Inbox = Field(...)
    message_type: str = Field(..., example="incoming")
    private: bool = Field(..., example=False)
    sender: Sender = Field(...)
    source_id: str | None = Field(None, example="134")
    event: str = Field(..., example="message_created")

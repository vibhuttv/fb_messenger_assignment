from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

import uuid

class MessageBase(BaseModel):
    content: str = Field(..., description="Content of the message")

class MessageCreate(MessageBase):
    sender_id: int = Field(..., description="ID of the sender")
    receiver_id: int = Field(..., description="ID of the receiver")

class MessageResponse(MessageBase):
    id: int = Field(..., description="Unique ID of the message")
    sender_id: int = Field(..., description="ID of the sender")
    receiver_id: int = Field(..., description="ID of the receiver")
    created_at: datetime = Field(..., description="Timestamp when message was created")
    conversation_id: uuid.UUID = Field(..., description="ID of the conversation")

class PaginatedMessageRequest(BaseModel):
    page: int = Field(1, description="Page number for pagination")
    limit: int = Field(20, description="Number of items per page")
    before_timestamp: Optional[datetime] = Field(None, description="Get messages before this timestamp")

class PaginatedMessageResponse(BaseModel):
    total: int = Field(..., description="Total number of messages")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    data: List[MessageResponse] = Field(..., description="List of messages") 
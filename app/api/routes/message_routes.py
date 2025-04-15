from fastapi import APIRouter, Depends, Query, Path, Body
from typing import Optional
from datetime import datetime

from app.controllers.message_controller import MessageController
from app.schemas.message import (
    MessageCreate, 
    MessageResponse, 
    PaginatedMessageResponse
)


import uuid
import logging
# Configure logger
logger = logging.getLogger("message_routes")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


router = APIRouter(prefix="/api/messages", tags=["Messages"])

@router.post("/", response_model=MessageResponse, status_code=201)
async def send_message(
    message: MessageCreate = Body(...),
    message_controller: MessageController = Depends()
): # -> MessageResponse:
    # return {"sux": 12}
    """
    Send a message from one user to another
    """
    return await message_controller.send_message(message)

@router.get("/conversation/{conversation_id}", response_model=PaginatedMessageResponse)
async def get_conversation_messages(
    conversation_id: uuid.UUID = Path(..., description="ID of the conversation"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Number of messages per page"),
    message_controller: MessageController = Depends()
) -> PaginatedMessageResponse:
    """
    Get all messages in a conversation with pagination
    """
    logger.info("MESSAGEROUTE - CONVERSATION")
    return await message_controller.get_conversation_messages(
        conversation_id=conversation_id,
        page=page,
        limit=limit
    )

@router.get("/conversation/{conversation_id}/before", response_model=PaginatedMessageResponse)
async def get_messages_before_timestamp(
    # conversation_id: int = Path(..., description="ID of the conversation"),
    conversation_id: uuid.UUID = Path(..., description="ID of the conversation"),
    before_timestamp: datetime = Query(..., description="Get messages before this timestamp"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(20, description="Number of messages per page"),
    message_controller: MessageController = Depends()
) -> PaginatedMessageResponse:
    """
    Get messages in a conversation before a specific timestamp with pagination
    """
    return await message_controller.get_messages_before_timestamp(
        conversation_id=conversation_id,
        before_timestamp=before_timestamp,
        page=page,
        limit=limit
    ) 
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status

from app.schemas.message import MessageCreate, MessageResponse, PaginatedMessageResponse

import uuid

from app.models.cassandra_models import ConversationModel, MessageModel

class MessageController:
    """
    Controller for handling message operations
    This is a stub that students will implement
    """
    
    async def send_message(self, message_data: MessageCreate) -> MessageResponse:
        """
        Send a message from one user to another
        
        Args:
            message_data: The message data including content, sender_id, and receiver_id
            
        Returns:
            The created message with metadata
        
        Raises:
            HTTPException: If message sending fails
        """
        
        try:
            # Retrieve or create a conversation between sender and receiver.
            conversation = await ConversationModel.create_or_get_conversation(
                message_data.sender_id, message_data.receiver_id
            )
            # Get conversation_id (the model returns key "id").
            conversation_id = conversation.get("conversation_id")
            msg = await MessageModel.create_message(
                conversation_id, message_data.sender_id, message_data.receiver_id, message_data.content
            )
            return MessageResponse(**msg)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
            
        # This is a stub - students will implement the actual logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Method not implemented"
        )
    
    async def get_conversation_messages(
        self, 
        conversation_id: uuid.UUID, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get all messages in a conversation with pagination
        
        Args:
            conversation_id: ID of the conversation
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        
        try:
            paginated_content = await MessageModel.get_conversation_messages(conversation_id, page, limit)
            return PaginatedMessageResponse(**paginated_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        # This is a stub - students will implement the actual logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Method not implemented"
        )
    
    async def get_messages_before_timestamp(
        self, 
        conversation_id: uuid.UUID, 
        before_timestamp: datetime,
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedMessageResponse:
        """
        Get messages in a conversation before a specific timestamp with pagination
        
        Args:
            conversation_id: ID of the conversation
            before_timestamp: Get messages before this timestamp
            page: Page number
            limit: Number of messages per page
            
        Returns:
            Paginated list of messages
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        
        try:
            messages_paginated = await MessageModel.get_messages_before_timestamp(conversation_id, before_timestamp, page, limit)
            return PaginatedMessageResponse(**messages_paginated)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        
        # This is a stub - students will implement the actual logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Method not implemented"
        ) 
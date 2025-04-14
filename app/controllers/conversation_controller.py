from fastapi import HTTPException, status

from app.schemas.conversation import ConversationResponse, PaginatedConversationResponse

from app.models.cassandra_models import ConversationModel

import uuid
from logging import logger

class ConversationController:
    """
    Controller for handling conversation operations
    This is a stub that students will implement
    """
    
    async def get_user_conversations(
        self, 
        user_id: int, 
        page: int = 1, 
        limit: int = 20
    ) -> PaginatedConversationResponse:
        """
        Get all conversations for a user with pagination
        
        Args:
            user_id: ID of the user
            page: Page number
            limit: Number of conversations per page
            
        Returns:
            Paginated list of conversations
            
        Raises:
            HTTPException: If user not found or access denied
        """
        
        try:
            conversations = await ConversationModel.get_user_conversations(user_id, page, limit)
            return PaginatedConversationResponse(**conversations)
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
    
    async def get_conversation(self, conversation_id: uuid.UUID) -> ConversationResponse:
        """
        Get a specific conversation by ID
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Conversation details
            
        Raises:
            HTTPException: If conversation not found or access denied
        """
        
        try:
            conv = await ConversationModel.get_conversation(conversation_id)
            return ConversationResponse(**conv)
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
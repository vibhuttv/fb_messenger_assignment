"""
Sample models for interacting with Cassandra tables.
Students should implement these models based on their database schema design.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.db.cassandra_client import cassandra_client
from app.schemas.message import MessageResponse
from logging import logger



def paginate_messages(all_messages, page, limit):
        """
        Paginate messages based on the page number and limit.
        
        Args:
            messages (List[Dict[str, Any]]): List of messages to paginate.
            page (int): Page number.
            limit (int): Number of messages per page.
        
        Returns:
            List[Dict[str, Any]]: Paginated list of messages.
        """
        start = (page - 1) * limit
        end = start + limit
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_result = all_messages[start_index:end_index]
        messages = []
        for row in paginated_result:
            messages.append(
                MessageResponse(
                    message_id=row.message_id,
                    conversation_id=row.conversation_id,
                    message_timestamp=row.message_timestamp,
                    sender_id=row.sender_id,
                    recipient_id=row.recipient_id,
                    content=row.content
                )
            )
        return {
            "page": page,
            "limit": limit,
            "total_messages": len(all_messages),
            "messages": messages
        }

class MessageModel:
    """
    Message model for interacting with the messages table.
    Students will implement this as part of the assignment.
    
    They should consider:
    - How to efficiently store and retrieve messages
    - How to handle pagination of results
    - How to filter messages by timestamp
    """
    
    

    
    # TODO: Implement the following methods
    
    
    
    @staticmethod
    # async def create_message(*args, **kwargs):
    async def create_message(
        conversation_id: uuid.UUID,
        # message_id: uuid.UUID,
        # message_tiestamp: datetime,
        sender_id: int,
        recipient_id: int,
        content: str):
        """
        Create a new message.
        
        Students should decide what parameters are needed based on their schema design.
        """
        
        message_timestamp = datetime.now()
        message_id = uuid.uuid4()
        
        
        try:
            query = """
            insert into messages_by_conversation 
            (conversation_id, message_id, message_timestamp, sender_id, recipient_id, content)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (conversation_id, message_id, message_timestamp, sender_id, recipient_id, content)
            cassandra_client.execute(query, params)
            
        except Exception as e:
            # Handle exceptions (e.g., log them, raise custom exceptions, etc.)
            logger.error("Error while inserting message: create_message")
            raise e
        
        try:
            # Update the conversation with the last message details.
            update_conversation = """
            update user_conversations
            SET last_message_content = %s, 
            last_message_at = %s
            where conversation_id = %s
            """
            
            params_conversation = (content, message_timestamp, conversation_id)
            cassandra_client.execute(update_conversation, params_conversation)
            
        except Exception as e:
            # Handle exceptions (e.g., log them, raise custom exceptions, etc.)
            logger.error("Error while inserting message: create_message")
            raise e
        
        return {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "message_timestamp": message_timestamp,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content
        }
                    
        # This is a stub - students will implement the actual logic
        raise NotImplementedError("This method needs to be implemented")
    
    @staticmethod
    # async def get_conversation_messages(*args, **kwargs):
    async def get_conversation_messages(
        conversation_id: uuid.UUID,
        page: int = 1,
        limit: int = 10,
    ):
        """
        Get messages for a conversation with pagination.
        
        Students should decide what parameters are needed and how to implement pagination.
        """
        
        query = """
        SELECT * 
        FROM messages_by_conversation 
        WHERE conversation_id = %s
        """
        
        params = (conversation_id,)
        messages = cassandra_client.execute(query, params)
        
        return paginate_messages(messages, page, limit)
    
        
        # This is a stub - students will implement the actual logic
        raise NotImplementedError("This method needs to be implemented")
    
    
    @staticmethod
    async def get_messages_before_timestamp(conversation_id: uuid.UUID, before_timestamp: datetime, page: int = 1, limit: int = 10):
        """
        Get messages before a timestamp with pagination.
        
        Students should decide how to implement filtering by timestamp with pagination.
        """
        
        query = """
        SELECT *
        FROM messages_by_conversation 
        WHERE conversation_id = %s AND message_timestamp < %s
        """
        params = (conversation_id, before_timestamp)
        messages = cassandra_client.execute(query, params)
        
        return paginate_messages(messages, page, limit)
        
        # This is a stub - students will implement the actual logic
        raise NotImplementedError("This method needs to be implemented")
    
    


class ConversationModel:
    """
    Conversation model for interacting with the conversations-related tables.
    Students will implement this as part of the assignment.
    
    They should consider:
    - How to efficiently store and retrieve conversations for a user
    - How to handle pagination of results
    - How to optimize for the most recent conversations
    """
    
    # TODO: Implement the following methods
    
    @staticmethod
    # async def get_user_conversations(*args, **kwargs):
    async def get_user_conversations(user_id: int, page: int = 1, limit: int = 10):
        """
        Get conversations for a user with pagination.
        
        Students should decide what parameters are needed and how to implement pagination.
        """
        
        query  = """
        SELECT *
        FROM user_conversations
        WHERE user_id = %s
        """
        params = (user_id,)
        all_messages = cassandra_client.execute(query, params)

        all_messages.sort(key=lambda k: k.get("last_message_at") or datetime.min, reverse=True)
        
        total = len(all_messages)
        start = (page - 1) * limit
        messages = all_messages[start:start + limit]
        
        conversations = []
        for row in messages:
            users = row.get("list_of_users", [])
            
            if len(users) >= 2:
                user1, user2 = sorted(users)[:2]
            elif len(users) == 1:
                user1 = users[0]
                user2 = None
            else:
                user1 = user2 = None
                
                
            conversations.append({
                "conversation_id": row.conversation_id,
                "user1_id": user1,
                "user2_id": user2,
                "last_message_at": row.last_message_at,
                "last_message_content": row.get("last_message_content")
            })
    
        
        return {
            "total": len(conversations),
            "page": page,
            "limit": limit,
            "conversations": conversations[start:start + limit]
        }
        
        
        # This is a stub - students will implement the actual logic
        raise NotImplementedError("This method needs to be implemented")
    
    @staticmethod
    async def get_conversation(conversation_id: uuid.UUID):
        """
        Get a conversation by ID.
        
        Students should decide what parameters are needed and what data to return.
        """
        
        query = """
        SELECT *
        FROM user_conversations
        WHERE conversation_id = %s
        """
        params = (conversation_id,)
        conversation = cassandra_client.execute(query, params)
        if not conversation:
            return None
        conversation = conversation[0]
        users = conversation.get("list_of_users", [])
        
        if len(users) >= 2:
            user1, user2 = sorted(users)[:2]
        elif len(users) == 1:
            user1 = users[0]
            user2 = None
        else:
            user1 = user2 = None
            
        
        return {
            "conversation_id": conversation.conversation_id,
            "user1_id": user1,
            "user2_id": user2,
            "last_message_at": conversation.get("last_message_at"),
            "last_message_content": conversation.get("last_message_content")
        }
        
        # This is a stub - students will implement the actual logic
        raise NotImplementedError("This method needs to be implemented")
    
    @staticmethod
    # async def create_or_get_conversation(*args, **kwargs):
    async def create_or_get_conversation(user1: int, user2: int):
    
        
        """
        Get an existing conversation between two users or create a new one.
        
        Students should decide how to handle this operation efficiently.
        """
        
        # Check if a conversation already exists between the two users
        query = """
        SELECT * 
        FROM conversations 
        WHERE list_of_users CONTAINS %s 
        ALLOW FILTERING
        """
        params = (user1,)
        conversation = cassandra_client.execute(query, params)
        
        for conv in conversation:
            if user2 in conv.get("list_of_users", []):
                return conv

        
        
        # If no conversation exists, create a new one
        conversation_id = uuid.uuid4()
        message_at = datetime.now()
        
        query = """
            INSERT INTO conversations 
            (conversation_id, list_of_users, created_at, last_message_at)
            VALUES (%s, %s, %s, %s)
        """
        
        params = (conversation_id, [user1, user2], message_at, message_at)
        cassandra_client.execute(query, params)
        
        return {
            "conversation_id": conversation_id,
            "list_of_users": [user1, user2],
            "created_at": message_at,
            "last_message_at": message_at,
            "last_message_content": None,
        }
        
        
        # This is a stub - students will implement the actual logic
        raise NotImplementedError("This method needs to be implemented") 
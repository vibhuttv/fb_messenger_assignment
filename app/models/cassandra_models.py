"""
Sample models for interacting with Cassandra tables.
Students should implement these models based on their database schema design.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.db.cassandra_client import cassandra_client
from app.schemas.message import MessageResponse
import logging


# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)


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
        
        logger.info("Here ---------")
        for row in paginated_result:
            logger.info("Check pagi")
            logger.info(row)
            messages.append(
                MessageResponse(
                    id=row["message_id"],
                    conversation_id=row["conversation_id"],
                    created_at=row["message_timestamp"],
                    sender_id=row["sender_id"],
                    receiver_id=row["recipient_id"],
                    content=row["content"]
                )
            )
            
        logger.info("Done with pagi")
        return {
            "page": page,
            "limit": limit,
            "total": len(all_messages),
            "data": messages
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
        sender_id: int,
        recipient_id: int,
        content: str):
        
        logger.info("Entered create_message method")
        """
        Create a new message.
        
        Students should decide what parameters are needed based on their schema design.
        """
        
        message_timestamp = datetime.utcnow()
        message_id = uuid.uuid4()
        
        logger.debug(f"Creating message with ID: {message_id}")
        
        
        try:
            query = """
            insert into messages_by_conversation 
            (conversation_id, message_timestamp, message_id, sender_id, recipient_id, content)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (conversation_id, message_timestamp, message_id, sender_id, recipient_id, content)
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
            # logger.error("Error while inserting message: create_message")
            raise e
        
        return {
            "id": message_id,
            "sender_id": sender_id,
            "receiver_id": recipient_id,
            "content": content,
            "created_at": message_timestamp,
            "conversation_id": conversation_id,
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
        
        logger.info("S1 - models - get_convo_message")
        
        query = """
        SELECT * 
        FROM messages_by_conversation 
        WHERE conversation_id = %s
        """
        
        params = (conversation_id,)
        messages = cassandra_client.execute(query, params)
        
        logger.info(messages)
        
        logger.info("S2 - models - get_convo_message")
        
        
        res = paginate_messages(messages, page, limit)
        
        # return {"total": len(messages), "page": page, "limit": limit, "data": res}
        return res
    
        
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
        
        logger.info("S1 - get_user_c")
        
        query = """SELECT *
        FROM user_conversations
        WHERE list_of_users CONTAINS %s 
        ALLOW FILTERING"""

        params = (user_id,)
        all_messages = cassandra_client.execute(query, params)
        
        logger.info("S2 - get_user_c")
        

        all_messages.sort(key=lambda k: k.get("last_message_at") or datetime.min, reverse=True)
        
        start = (page - 1) * limit
        messages = all_messages[start:start + limit]
        
        logger.info("S3 - get_user_c")
        
        
        conversations = []
        for row in messages:
            logger.info(row)
            users = row.get("list_of_users", [])
            
            if len(users) >= 2:
                user1, user2 = sorted(users)[:2]
            elif len(users) == 1:
                user1 = users[0]
                user2 = None
            else:
                user1 = user2 = None
                
            

                
            conversations.append({
                "id": row["conversation_id"],
                "user1_id": user1,
                "user2_id": user2,
                "last_message_at": row["last_message_at"],
                "last_message_content": row["last_message_content"]
            })
    
        logger.info("S4 - get_user_c")
        
        return {
            "total": len(all_messages),
            "page": page,
            "limit": limit,
            "data": conversations[start:start + limit]
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
            
        logger.info("S1 - get_c")
        return {
            "id": conversation.get("conversation_id"),
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
        
        logger.info("S1 - Entered create_or_get_conversation method")
        
        # Check if a conversation already exists between the two users
        query = """
        SELECT * 
        FROM user_conversations 
        WHERE list_of_users CONTAINS %s 
        ALLOW FILTERING
        """
        params = (user1,)
        
        logger.info("S2 - Entered create_or_get_conversation method")

        conversation = cassandra_client.execute(query, params)
        
        logger.info("S! - Entered create_or_get_conversation method")
        
        
        for conv in conversation:
            logger.info(f"Conversation: {conv}")
            if user2 in conv.get("list_of_users", []):
                logger.info("User2 found in conversation")
                return conv
            
        logger.info("S3 - Entered create_or_get_conversation method")
            

        
        
        # If no conversation exists, create a new one
        conversation_id = uuid.uuid4()
        message_at = datetime.now()
        
        logger.info("S4 - Entered create_or_get_conversation method")
        
        
        query = """
            INSERT INTO user_conversations 
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
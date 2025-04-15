


# Cassandra Schema for Facebook Messenger MVP


## Table 1: messages_by_conversation
For: Fetching all messages in a conversation (recent first) and pagination

- Partition Key: `conversation_id`
- Clustering Columns: `message_timestamp DESC`, `message_id`
- Supports: Retrieving all messages in a conversation and pagination.

```sql
CREATE TABLE IF NOT EXISTS messages_by_conversation (
    conversation_id UUID,
    message_timestamp TIMESTAMP,
    message_id UUID,
    sender_id INT,
    recipient_id INT,
    content TEXT,
    PRIMARY KEY ((conversation_id), message_timestamp, message_id)
) WITH CLUSTERING ORDER BY (message_timestamp DESC, message_id ASC);
```


## Table 2: user_conversions
For: Fetching all conversations of a user, ordered by recent activity

- Partition Key: `user_id`
- Clustering Columns: `last_message_timestamp DESC`, `conversation_id`
- Supports: Showing recent conversations per user.

```sql
-- CREATE TABLE IF NOT EXISTS user_conversions (
--     user_id UUID,
--     last_message_timestamp TIMESTAMP,
--     conversation_id UUID,
--     participant_id UUID,
--     PRIMARY KEY ((user_id), last_message_timestamp, conversation_id)
-- ) WITH CLUSTERING ORDER BY (last_message_timestamp DESC, conversation_id ASC);
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id UUID PRIMARY KEY,
    list_of_users LIST<INT>,
    last_message_content TEXT,
    last_message_at TIMESTAMP,
    created_at TIMESTAMP
);
```


## Table 3: messages_by_id
For: Fast message lookup if needed (optional for this MVP)

- Primary Key: `message_id`

```sql
CREATE TABLE IF NOT EXISTS messages_by_id (
    message_id UUID,
    conversation_id UUID,
    sender_id UUID,
    recipient_id UUID,
    content TEXT,
    message_timestamp TIMESTAMP,
    PRIMARY KEY (message_id)
);
```


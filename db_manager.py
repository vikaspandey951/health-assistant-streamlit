import streamlit as st
import pymongo
from bson.objectid import ObjectId
import datetime

# Connect to MongoDB using the secret
@st.cache_resource
def get_db_connection():
    client = pymongo.MongoClient(st.secrets["MONGO_URI"])
    db = client.health_assistant_db
    return db

db = get_db_connection()
users_collection = db.users
conversations_collection = db.conversations  # <-- NEW
messages_collection = db.messages          # <-- RENAMED

# --- User Functions (Same as before) ---
def get_user(username):
    return users_collection.find_one({"username": username})

def create_user(username, hashed_password):
    return users_collection.insert_one({"username": username, "password": hashed_password})

# --- NEW Conversation Functions ---
def create_conversation(username, title):
    """Creates a new conversation and returns its ID."""
    result = conversations_collection.insert_one({
        "username": username,
        "title": title,
        "timestamp": datetime.datetime.now()
    })
    return result.inserted_id

def get_conversations(username):
    """Gets all conversations for a user, sorted by newest first."""
    return list(conversations_collection.find(
        {"username": username}
    ).sort("timestamp", -1))

# --- MODIFIED Message Functions ---
def save_message(conversation_id, message_object):
    """Saves a message (user or assistant) to a specific conversation."""
    return messages_collection.insert_one({
        "conversation_id": str(conversation_id),
        "message": message_object,
        "timestamp": datetime.datetime.now()
    })

def get_messages(conversation_id):
    """Gets all messages for a specific conversation, sorted by oldest first."""
    return list(messages_collection.find(
        {"conversation_id": str(conversation_id)}
    ).sort("timestamp"))
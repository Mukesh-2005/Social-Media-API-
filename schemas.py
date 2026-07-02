# schemas.py
from pydantic import BaseModel
from datetime import datetime

#  USER SCHEMAS 
class UserCreate(BaseModel):
    """Schema for creating a user"""
    username: str
    email: str
    password: str
    bio: str = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "mukesh_codes",
                "email": "mukesh@example.com",
                "password": "password123",
                "bio": "Python Developer"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: str = None
    bio: str = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    bio: str
    created_at: datetime
    followers_count: int
    following_count: int
    
    class Config:
        from_attributes = True


#  POST SCHEMAS 

class PostCreate(BaseModel):
    """Schema for creating a post"""
    content: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Learning FastAPI is fun!"
            }
        }


class PostUpdate(BaseModel):
    """Schema for updating a post"""
    content: str


class PostResponse(BaseModel):
    """Schema for post response"""
    id: int
    content: str
    user_id: int
    likes_count: int
    comments_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


#  COMMENT SCHEMAS 
class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    content: str


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: str


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: int
    content: str
    post_id: int
    user_id: int
    likes_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


#  MESSAGE SCHEMA 

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
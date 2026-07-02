# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class UserModel(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    
    # Relationships
    posts = relationship("PostModel", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("CommentModel", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("LikeModel", back_populates="user", cascade="all, delete-orphan")
    followers = relationship(
        "FollowModel",
        foreign_keys="FollowModel.following_id",
        back_populates="following_user",
        cascade="all, delete-orphan"
    )
    following = relationship(
        "FollowModel",
        foreign_keys="FollowModel.follower_id",
        back_populates="follower_user",
        cascade="all, delete-orphan"
    )


class PostModel(Base):
    """Post database model"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    author = relationship("UserModel", back_populates="posts")
    comments = relationship("CommentModel", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("LikeModel", back_populates="post", cascade="all, delete-orphan")


class CommentModel(Base):
    """Comment database model"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    post = relationship("PostModel", back_populates="comments")
    author = relationship("UserModel", back_populates="comments")


class LikeModel(Base):
    """Like database model"""
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="likes")
    post = relationship("PostModel", back_populates="likes")


class FollowModel(Base):
    """Follow database model"""
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), index=True)
    following_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    follower_user = relationship(
        "UserModel",
        foreign_keys=[follower_id],
        back_populates="following"
    )
    following_user = relationship(
        "UserModel",
        foreign_keys=[following_id],
        back_populates="followers"
    )
# routers/posts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import PostModel, UserModel, LikeModel
from schemas import PostCreate, PostUpdate, PostResponse, MessageResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/posts", tags=["Posts"])


#  CREATE POST (POST /posts)
@router.post("", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Create a new post
    
    Query params:
    - user_id: ID of user creating the post
    """
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Validate content is not empty
    if not post.content or not post.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content cannot be empty"
        )
    
    # Create new post
    new_post = PostModel(
        content=post.content,
        user_id=user_id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    logger.info(f" Post created: ID {new_post.id} by user {user_id}")
    return new_post


#  GET SINGLE POST (GET /posts/{post_id})
@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    logger.info(f"Post fetched: ID {post_id}")
    return post


#  GET ALL POSTS (GET /posts)
@router.get("", response_model=list[PostResponse])
def get_all_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all posts with pagination
    
    Query params:
    - skip: Number of posts to skip (default: 0)
    - limit: Number of posts to return (default: 10)
    """
    posts = db.query(PostModel).offset(skip).limit(limit).all()
    
    logger.info(f" Fetched {len(posts)} posts (skip={skip}, limit={limit})")
    return posts


#  GET POSTS BY USER (GET /posts/user/{user_id})
@router.get("/user/{user_id}", response_model=list[PostResponse])
def get_user_posts(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all posts by a specific user
    
    Query params:
    - user_id: User ID
    - skip: Number of posts to skip (default: 0)
    - limit: Number of posts to return (default: 10)
    """
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    posts = db.query(PostModel).filter(
        PostModel.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    logger.info(f" Fetched {len(posts)} posts from user {user_id}")
    return posts


#  UPDATE POST (PUT /posts/{post_id})
@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_update: PostUpdate, user_id: int, db: Session = Depends(get_db)):
    """
    Update a post
    
    Query params:
    - user_id: ID of user (must own the post)
    """
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    # Check if user owns this post
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )
    
    # Validate content
    if not post_update.content or not post_update.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content cannot be empty"
        )
    
    post.content = post_update.content
    
    db.commit()
    db.refresh(post)
    
    logger.info(f" Post updated: ID {post_id}")
    return post


#  DELETE POST (DELETE /posts/{post_id})
@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Delete a post
    
    Query params:
    - user_id: ID of user (must own the post)
    
    ⚠️ This will also delete all comments and likes on this post
    """
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    # Check if user owns this post
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )
    
    db.delete(post)
    db.commit()
    
    logger.info(f" Post deleted: ID {post_id}")
    return {"message": f"Post {post_id} deleted successfully"}


#  LIKE POST (POST /posts/{post_id}/like)
@router.post("/{post_id}/like", response_model=MessageResponse, status_code=201)
def like_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Like a post
    
    Query params:
    - user_id: ID of user liking the post
    """
    # Check if post exists
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check if already liked
    existing_like = db.query(LikeModel).filter(
        LikeModel.post_id == post_id,
        LikeModel.user_id == user_id
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already liked this post"
        )
    
    # Create like
    new_like = LikeModel(
        user_id=user_id,
        post_id=post_id
    )
    
    # Increment likes_count
    post.likes_count += 1
    
    db.add(new_like)
    db.commit()
    
    logger.info(f"Post {post_id} liked by user {user_id}")
    return {"message": "Post liked successfully"}


# UNLIKE POST (DELETE /posts/{post_id}/like)
@router.delete("/{post_id}/like", response_model=MessageResponse)
def unlike_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Unlike a post
    
    Query params:
    - user_id: ID of user unliking the post
    """
    # Check if post exists
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    # Find and delete the like
    like = db.query(LikeModel).filter(
        LikeModel.post_id == post_id,
        LikeModel.user_id == user_id
    ).first()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't liked this post"
        )
    
    # Decrement likes_count
    post.likes_count = max(0, post.likes_count - 1)
    
    db.delete(like)
    db.commit()
    
    logger.info(f" Post {post_id} unliked by user {user_id}")
    return {"message": "Post unliked successfully"}


# GET LIKES COUNT (GET /posts/{post_id}/likes-count)
@router.get("/{post_id}/likes-count", response_model=dict)
def get_likes_count(post_id: int, db: Session = Depends(get_db)):
    """Get number of likes on a post"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    return {"post_id": post_id, "likes_count": post.likes_count}


#  GET POST WITH AUTHOR (GET /posts/{post_id}/detailed)
@router.get("/{post_id}/detailed", response_model=dict)
def get_post_detailed(post_id: int, db: Session = Depends(get_db)):
    """Get post with author details"""
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    return {
        "id": post.id,
        "content": post.content,
        "likes_count": post.likes_count,
        "comments_count": post.comments_count,
        "created_at": post.created_at,
        "author": {
            "id": post.author.id,
            "username": post.author.username,
            "email": post.author.email,
            "bio": post.author.bio
        }
    }
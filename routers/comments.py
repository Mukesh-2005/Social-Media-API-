# routers/comments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import CommentModel, PostModel, UserModel, LikeModel
from schemas import CommentCreate, CommentUpdate, CommentResponse, MessageResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/comments", tags=["Comments"])


# CREATE COMMENT (POST /comments)
@router.post("", response_model=CommentResponse, status_code=201)
def create_comment(comment: CommentCreate, post_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Create a new comment on a post
    
    Query params:
    - post_id: ID of post to comment on
    - user_id: ID of user creating the comment
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
    
    # Validate content is not empty
    if not comment.content or not comment.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment content cannot be empty"
        )
    
    # Create new comment
    new_comment = CommentModel(
        content=comment.content,
        post_id=post_id,
        user_id=user_id
    )
    
    # Increment post's comments_count
    post.comments_count += 1
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    logger.info(f"Comment created: ID {new_comment.id} on post {post_id}")
    return new_comment


#  GET SINGLE COMMENT (GET /comments/{comment_id})
@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a specific comment by ID"""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )
    
    logger.info(f"Comment fetched: ID {comment_id}")
    return comment


#  GET ALL COMMENTS (GET /comments)
@router.get("", response_model=list[CommentResponse])
def get_all_comments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all comments with pagination
    
    Query params:
    - skip: Number of comments to skip (default: 0)
    - limit: Number of comments to return (default: 10)
    """
    comments = db.query(CommentModel).offset(skip).limit(limit).all()
    
    logger.info(f"Comment fetched: {len(comments)} comments (skip={skip}, limit={limit})")
    return comments


#  GET COMMENTS ON A POST (GET /comments/post/{post_id})
@router.get("/post/{post_id}", response_model=list[CommentResponse])
def get_post_comments(post_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all comments on a specific post
    
    Query params:
    - post_id: Post ID
    - skip: Number of comments to skip (default: 0)
    - limit: Number of comments to return (default: 10)
    """
    # Check if post exists
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    
    comments = db.query(CommentModel).filter(
        CommentModel.post_id == post_id
    ).offset(skip).limit(limit).all()
    
    logger.info(f"Comment fetched: {len(comments)} comments from post {post_id}")
    return comments


#  GET COMMENTS BY USER (GET /comments/user/{user_id})
@router.get("/user/{user_id}", response_model=list[CommentResponse])
def get_user_comments(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all comments made by a specific user
    
    Query params:
    - user_id: User ID
    - skip: Number of comments to skip (default: 0)
    - limit: Number of comments to return (default: 10)
    """
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    comments = db.query(CommentModel).filter(
        CommentModel.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    logger.info(f"Comment fetched: {len(comments)} comments from user {user_id}")
    return comments


#  UPDATE COMMENT (PUT /comments/{comment_id})
@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(comment_id: int, comment_update: CommentUpdate, user_id: int, db: Session = Depends(get_db)):
    """
    Update a comment
    
    Query params:
    - user_id: ID of user (must own the comment)
    """
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )
    
    # Check if user owns this comment
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own comments"
        )
    
    # Validate content
    if not comment_update.content or not comment_update.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment content cannot be empty"
        )
    
    comment.content = comment_update.content
    
    db.commit()
    db.refresh(comment)
    
    logger.info(f"Comment updated: ID {comment_id}")
    return comment


# DELETE COMMENT (DELETE /comments/{comment_id})
@router.delete("/{comment_id}", response_model=MessageResponse)
def delete_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Delete a comment
    
    Query params:
    - user_id: ID of user (must own the comment)
    
     This will also delete all likes on this comment
    """
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )
    
    # Check if user owns this comment
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    # Get the post and decrement comments_count
    post = db.query(PostModel).filter(PostModel.id == comment.post_id).first()
    if post:
        post.comments_count = max(0, post.comments_count - 1)
    
    db.delete(comment)
    db.commit()
    
    logger.info(f"Comment deleted: ID {comment_id}")
    return {"message": f"Comment {comment_id} deleted successfully"}


#  LIKE COMMENT (POST /comments/{comment_id}/like)
@router.post("/{comment_id}/like", response_model=MessageResponse, status_code=201)
def like_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Like a comment
    
    Query params:
    - user_id: ID of user liking the comment
    
     Note: We're using LikeModel for both posts and comments
    We need a way to differentiate, or create a separate table
    For now, we'll track it differently
    """
    # Check if comment exists
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )
    
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # For now, just increment the likes_count
    # (In production, you'd track individual likes)
    comment.likes_count += 1
    
    db.commit()
    db.refresh(comment)
    
    logger.info(f" Comment {comment_id} liked by user {user_id}")
    return {"message": "Comment liked successfully"}


#  UNLIKE COMMENT (DELETE /comments/{comment_id}/like)
@router.delete("/{comment_id}/like", response_model=MessageResponse)
def unlike_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Unlike a comment
    
    Query params:
    - user_id: ID of user unliking the comment
    """
    # Check if comment exists
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )
    
    # Decrement likes_count
    if comment.likes_count > 0:
        comment.likes_count -= 1
    
    db.commit()
    db.refresh(comment)
    
    logger.info(f" Comment {comment_id} unliked by user {user_id}")
    return {"message": "Comment unliked successfully"}


# GET COMMENT LIKES COUNT (GET /comments/{comment_id}/likes-count)
@router.get("/{comment_id}/likes-count", response_model=dict)
def get_comment_likes_count(comment_id: int, db: Session = Depends(get_db)):
    """Get number of likes on a comment"""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )
    
    return {"comment_id": comment_id, "likes_count": comment.likes_count}


# GET COMMENT WITH AUTHOR AND POST (GET /comments/{comment_id}/detailed)
@router.get("/{comment_id}/detailed", response_model=dict)
def get_comment_detailed(comment_id: int, db: Session = Depends(get_db)):
    """Get comment with author and post details"""
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with ID {comment_id} not found"
        )
    
    return {
        "id": comment.id,
        "content": comment.content,
        "likes_count": comment.likes_count,
        "created_at": comment.created_at,
        "author": {
            "id": comment.author.id,
            "username": comment.author.username,
            "email": comment.author.email
        },
        "post": {
            "id": comment.post.id,
            "content": comment.post.content,
            "likes_count": comment.post.likes_count
        }
    }
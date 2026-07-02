# routers/follows.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import FollowModel, UserModel
from schemas import UserResponse, MessageResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/follows", tags=["Follows"])


#  FOLLOW USER (POST /follows)
@router.post("", response_model=MessageResponse, status_code=201)
def follow_user(follower_id: int, following_id: int, db: Session = Depends(get_db)):
    """
    Follow a user
    
    Query params:
    - follower_id: ID of user doing the following
    - following_id: ID of user to follow
    """
    # Check if both users exist
    follower = db.query(UserModel).filter(UserModel.id == follower_id).first()
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {follower_id} not found"
        )
    
    following = db.query(UserModel).filter(UserModel.id == following_id).first()
    if not following:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {following_id} not found"
        )
    
    # Cannot follow yourself
    if follower_id == following_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    # Check if already following
    existing_follow = db.query(FollowModel).filter(
        FollowModel.follower_id == follower_id,
        FollowModel.following_id == following_id
    ).first()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {follower_id} already follows user {following_id}"
        )
    
    # Create follow relationship
    new_follow = FollowModel(
        follower_id=follower_id,
        following_id=following_id
    )
    
    # Update follower and following counts
    follower.following_count += 1
    following.followers_count += 1
    
    db.add(new_follow)
    db.commit()
    
    logger.info(f"User {follower_id} followed user {following_id}")
    return {"message": f"User {follower_id} followed user {following_id}"}


# UNFOLLOW USER (DELETE /follows)
@router.delete("", response_model=MessageResponse)
def unfollow_user(follower_id: int, following_id: int, db: Session = Depends(get_db)):
    """
    Unfollow a user
    
    Query params:
    - follower_id: ID of user doing the unfollowing
    - following_id: ID of user to unfollow
    """
    # Check if users exist
    follower = db.query(UserModel).filter(UserModel.id == follower_id).first()
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {follower_id} not found"
        )
    
    following = db.query(UserModel).filter(UserModel.id == following_id).first()
    if not following:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {following_id} not found"
        )
    
    # Find follow relationship
    follow_relationship = db.query(FollowModel).filter(
        FollowModel.follower_id == follower_id,
        FollowModel.following_id == following_id
    ).first()
    
    if not follow_relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {follower_id} is not following user {following_id}"
        )
    
    # Update follower and following counts
    follower.following_count = max(0, follower.following_count - 1)
    following.followers_count = max(0, following.followers_count - 1)
    
    db.delete(follow_relationship)
    db.commit()
    
    logger.info(f" User {follower_id} unfollowed user {following_id}")
    return {"message": f"User {follower_id} unfollowed user {following_id}"}


#  GET FOLLOWERS (GET /follows/{user_id}/followers)
@router.get("/{user_id}/followers", response_model=list[UserResponse])
def get_followers(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all followers of a user
    
    Query params:
    - user_id: User ID
    - skip: Number of followers to skip (default: 0)
    - limit: Number of followers to return (default: 10)
    """
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get all follow relationships where this user is the followed person
    followers = db.query(UserModel).join(
        FollowModel,
        FollowModel.follower_id == UserModel.id
    ).filter(
        FollowModel.following_id == user_id
    ).offset(skip).limit(limit).all()
    
    logger.info(f" Fetched {len(followers)} followers of user {user_id}")
    return followers


# GET FOLLOWING (GET /follows/{user_id}/following)
@router.get("/{user_id}/following", response_model=list[UserResponse])
def get_following(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all users that a user is following
    
    Query params:
    - user_id: User ID
    - skip: Number of users to skip (default: 0)
    - limit: Number of users to return (default: 10)
    """
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get all follow relationships where this user is the follower
    following = db.query(UserModel).join(
        FollowModel,
        FollowModel.following_id == UserModel.id
    ).filter(
        FollowModel.follower_id == user_id
    ).offset(skip).limit(limit).all()
    
    logger.info(f" Fetched {len(following)} users following user {user_id}")
    return following


#  CHECK IF FOLLOWING (GET /follows/check)
@router.get("/check", response_model=dict)
def check_following(follower_id: int, following_id: int, db: Session = Depends(get_db)):
    """
    Check if one user follows another
    
    Query params:
    - follower_id: User ID of potential follower
    - following_id: User ID of potential following
    
    Returns: {is_following: true/false}
    """
    # Check if users exist
    follower = db.query(UserModel).filter(UserModel.id == follower_id).first()
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {follower_id} not found"
        )
    
    following = db.query(UserModel).filter(UserModel.id == following_id).first()
    if not following:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {following_id} not found"
        )
    
    # Check follow relationship
    follow_relationship = db.query(FollowModel).filter(
        FollowModel.follower_id == follower_id,
        FollowModel.following_id == following_id
    ).first()
    
    is_following = follow_relationship is not None
    
    logger.info(f" Check: User {follower_id} follows {following_id} = {is_following}")
    return {"is_following": is_following}


# GET FOLLOWERS COUNT (GET /follows/{user_id}/followers-count)
@router.get("/{user_id}/followers-count", response_model=dict)
def get_followers_count(user_id: int, db: Session = Depends(get_db)):
    """Get the number of followers for a user"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return {
        "user_id": user_id,
        "username": user.username,
        "followers_count": user.followers_count
    }


#  GET FOLLOWING COUNT (GET /follows/{user_id}/following-count)
@router.get("/{user_id}/following-count", response_model=dict)
def get_following_count(user_id: int, db: Session = Depends(get_db)):
    """Get the number of users that a user is following"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return {
        "user_id": user_id,
        "username": user.username,
        "following_count": user.following_count
    }


#  GET MUTUAL FOLLOWERS (GET /follows/mutual)
@router.get("/mutual/{user_id1}/{user_id2}", response_model=list[UserResponse])
def get_mutual_followers(user_id1: int, user_id2: int, db: Session = Depends(get_db)):
    """
    Get users that both user_id1 and user_id2 follow
    
    Path params:
    - user_id1: First user ID
    - user_id2: Second user ID
    """
    # Check if users exist
    user1 = db.query(UserModel).filter(UserModel.id == user_id1).first()
    if not user1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id1} not found"
        )
    
    user2 = db.query(UserModel).filter(UserModel.id == user_id2).first()
    if not user2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id2} not found"
        )
    
    # Get users followed by user1
    following1 = db.query(UserModel).join(
        FollowModel,
        FollowModel.following_id == UserModel.id
    ).filter(
        FollowModel.follower_id == user_id1
    ).all()
    
    # Get users followed by user2
    following2 = db.query(UserModel).join(
        FollowModel,
        FollowModel.following_id == UserModel.id
    ).filter(
        FollowModel.follower_id == user_id2
    ).all()
    
    # Find mutual (intersection)
    following1_ids = {user.id for user in following1}
    mutual = [user for user in following2 if user.id in following1_ids]
    
    logger.info(f" Found {len(mutual)} mutual followers between user {user_id1} and {user_id2}")
    return mutual


# GET USER STATS (GET /follows/{user_id}/stats)
@router.get("/{user_id}/stats", response_model=dict)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get follow stats for a user"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return {
        "user_id": user_id,
        "username": user.username,
        "followers_count": user.followers_count,
        "following_count": user.following_count,
        "created_at": user.created_at
    }
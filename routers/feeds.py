# routers/feeds.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import get_db
from models import PostModel, UserModel, FollowModel, LikeModel, CommentModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feeds", tags=["Feeds"])


#  GET USER FEED (GET /feeds/{user_id})
@router.get("/{user_id}", response_model=list[dict])
def get_user_feed(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get personalized feed for a user
    Shows posts from users they follow
    
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
    
    # Get list of users that this user follows
    following_ids = db.query(FollowModel.following_id).filter(
        FollowModel.follower_id == user_id
    ).all()
    
    following_ids = [f[0] for f in following_ids]
    
    if not following_ids:
        logger.info(f" User {user_id} is not following anyone")
        return []
    
    # Get posts from followed users, ordered by newest first
    posts = db.query(PostModel).filter(
        PostModel.user_id.in_(following_ids)
    ).order_by(desc(PostModel.created_at)).offset(skip).limit(limit).all()
    
    # Format response with author details
    feed = []
    for post in posts:
        feed.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched feed for user {user_id}: {len(feed)} posts")
    return feed


# GET TIMELINE (GET /feeds/{user_id}/timeline)
@router.get("/{user_id}/timeline", response_model=list[dict])
def get_user_timeline(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all posts by a specific user (their timeline)
    
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
    
    # Get all posts by this user, ordered by newest first
    posts = db.query(PostModel).filter(
        PostModel.user_id == user_id
    ).order_by(desc(PostModel.created_at)).offset(skip).limit(limit).all()
    
    # Format response
    timeline = []
    for post in posts:
        timeline.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched timeline for user {user_id}: {len(timeline)} posts")
    return timeline


# GET TRENDING POSTS (GET /feeds/trending)
@router.get("/trending/posts", response_model=list[dict])
def get_trending_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get trending posts (most liked posts)
    
    Query params:
    - skip: Number of posts to skip (default: 0)
    - limit: Number of posts to return (default: 10)
    """
    # Get posts ordered by likes_count descending
    posts = db.query(PostModel).order_by(
        desc(PostModel.likes_count)
    ).offset(skip).limit(limit).all()
    
    # Format response
    trending = []
    for post in posts:
        trending.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched trending posts: {len(trending)} posts")
    return trending


# GET RECENT POSTS (GET /feeds/recent)
@router.get("/recent/posts", response_model=list[dict])
def get_recent_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get recent posts (newest first)
    
    Query params:
    - skip: Number of posts to skip (default: 0)
    - limit: Number of posts to return (default: 10)
    """
    # Get posts ordered by created_at descending (newest first)
    posts = db.query(PostModel).order_by(
        desc(PostModel.created_at)
    ).offset(skip).limit(limit).all()
    
    # Format response
    recent = []
    for post in posts:
        recent.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched recent posts: {len(recent)} posts")
    return recent


#  GET MOST COMMENTED POSTS (GET /feeds/most-commented)
@router.get("/most-commented/posts", response_model=list[dict])
def get_most_commented_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get posts with most comments
    
    Query params:
    - skip: Number of posts to skip (default: 0)
    - limit: Number of posts to return (default: 10)
    """
    # Get posts ordered by comments_count descending
    posts = db.query(PostModel).order_by(
        desc(PostModel.comments_count)
    ).offset(skip).limit(limit).all()
    
    # Format response
    most_commented = []
    for post in posts:
        most_commented.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched most commented posts: {len(most_commented)} posts")
    return most_commented


#  GET POSTS LIKED BY USER (GET /feeds/{user_id}/liked-posts)
@router.get("/{user_id}/liked-posts", response_model=list[dict])
def get_user_liked_posts(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all posts liked by a specific user
    
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
    
    # Get all posts liked by this user
    liked_posts = db.query(PostModel).join(
        LikeModel,
        LikeModel.post_id == PostModel.id
    ).filter(
        LikeModel.user_id == user_id
    ).order_by(desc(LikeModel.created_at)).offset(skip).limit(limit).all()
    
    # Format response
    posts = []
    for post in liked_posts:
        posts.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched {len(posts)} liked posts by user {user_id}")
    return posts


#  GET TRENDING USERS (GET /feeds/trending-users)
@router.get("/trending/users", response_model=list[dict])
def get_trending_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get trending users (most followers)
    
    Query params:
    - skip: Number of users to skip (default: 0)
    - limit: Number of users to return (default: 10)
    """
    # Get users ordered by followers_count descending
    users = db.query(UserModel).order_by(
        desc(UserModel.followers_count)
    ).offset(skip).limit(limit).all()
    
    # Format response
    trending_users = []
    for user in users:
        trending_users.append({
            "id": user.id,
            "username": user.username,
            "bio": user.bio,
            "followers_count": user.followers_count,
            "following_count": user.following_count,
            "created_at": user.created_at
        })
    
    logger.info(f"Fetched trending users: {len(trending_users)} users")
    return trending_users


#  GET FEED STATISTICS (GET /feeds/{user_id}/stats)
@router.get("/{user_id}/stats", response_model=dict)
def get_feed_stats(user_id: int, db: Session = Depends(get_db)):
    """Get statistics for a user's feed"""
    # Check if user exists
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Count user's posts
    user_posts_count = db.query(func.count(PostModel.id)).filter(
        PostModel.user_id == user_id
    ).scalar()
    
    # Count user's total likes received
    total_likes_received = db.query(func.sum(PostModel.likes_count)).filter(
        PostModel.user_id == user_id
    ).scalar() or 0
    
    # Count user's total comments received
    total_comments_received = db.query(func.sum(PostModel.comments_count)).filter(
        PostModel.user_id == user_id
    ).scalar() or 0
    
    # Count posts liked by user
    posts_liked_by_user = db.query(func.count(LikeModel.id)).filter(
        LikeModel.user_id == user_id
    ).scalar()
    
    # Count comments made by user
    comments_by_user = db.query(func.count(CommentModel.id)).filter(
        CommentModel.user_id == user_id
    ).scalar()
    
    return {
        "user_id": user_id,
        "username": user.username,
        "followers_count": user.followers_count,
        "following_count": user.following_count,
        "posts_created": user_posts_count,
        "total_likes_received": total_likes_received,
        "total_comments_received": total_comments_received,
        "posts_liked_by_user": posts_liked_by_user,
        "comments_made_by_user": comments_by_user
    }


#  GET MUTUAL FRIENDS FEED (GET /feeds/mutual-feed)
@router.get("/mutual-feed/{user_id1}/{user_id2}", response_model=list[dict])
def get_mutual_friends_feed(user_id1: int, user_id2: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get posts from users that both user_id1 and user_id2 follow
    
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
    following1 = db.query(FollowModel.following_id).filter(
        FollowModel.follower_id == user_id1
    ).all()
    following1_ids = [f[0] for f in following1]
    
    # Get users followed by user2
    following2 = db.query(FollowModel.following_id).filter(
        FollowModel.follower_id == user_id2
    ).all()
    following2_ids = [f[0] for f in following2]
    
    # Find mutual
    mutual_ids = set(following1_ids) & set(following2_ids)
    
    if not mutual_ids:
        logger.info(f" No mutual friends between user {user_id1} and {user_id2}")
        return []
    
    # Get posts from mutual friends
    posts = db.query(PostModel).filter(
        PostModel.user_id.in_(list(mutual_ids))
    ).order_by(desc(PostModel.created_at)).offset(skip).limit(limit).all()
    
    # Format response
    feed = []
    for post in posts:
        feed.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched mutual feed: {len(feed)} posts from mutual friends")
    return feed


#  GET EXPLORED FEED (GET /feeds/explore)
@router.get("/explore/posts", response_model=list[dict])
def get_explore_feed(user_id: int = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get posts from users not followed by the current user (explore/discover)
    
    Query params:
    - user_id: Current user ID (optional)
    - skip: Number of posts to skip (default: 0)
    - limit: Number of posts to return (default: 10)
    """
    if user_id:
        # Get users this user follows
        following_ids = db.query(FollowModel.following_id).filter(
            FollowModel.follower_id == user_id
        ).all()
        following_ids = [f[0] for f in following_ids]
        following_ids.append(user_id)  # Also exclude their own posts
        
        # Get posts from users NOT followed
        posts = db.query(PostModel).filter(
            ~PostModel.user_id.in_(following_ids)
        ).order_by(desc(PostModel.likes_count)).offset(skip).limit(limit).all()
    else:
        # Just get popular posts for anonymous users
        posts = db.query(PostModel).order_by(
            desc(PostModel.likes_count)
        ).offset(skip).limit(limit).all()
    
    # Format response
    explore = []
    for post in posts:
        explore.append({
            "id": post.id,
            "content": post.content,
            "likes_count": post.likes_count,
            "comments_count": post.comments_count,
            "created_at": post.created_at,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "bio": post.author.bio
            }
        })
    
    logger.info(f" Fetched explore feed: {len(explore)} posts")
    return explore
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt

# ✅ FIX: Capital 'L' in getLogger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ============================================
# ✅ PART 1: CONFIGURATION
# ============================================

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ============================================
# ✅ PART 2: DATA MODELS
# ============================================

# User Models
class User(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# Post Models
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Comment Models
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# ✅ PART 3: SIMULATED DATABASE
# ============================================

# Simulate database storage
users_db = {}
posts_db = {}
comments_db = {}
next_post_id = 1
next_comment_id = 1


# ============================================
# ✅ PART 4: AUTHENTICATION FUNCTIONS
# ============================================

def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Token created for user: {data.get('sub')}")
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            logger.warning("Token has no username")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = users_db.get(username)
        if user is None:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.debug(f"Current user: {username}")
        return user
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================
# ✅ PART 5: CREATE FASTAPI APP
# ============================================

app = FastAPI(
    title="Blog Platform",
    description="A Blog Platform API with REST principles",
    version="1.0.0"
)


# ============================================
# ✅ PART 6: AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(user: UserRegister):
    """Register new user"""
    logger.info(f"Register attempt for user: {user.username}")
    
    # Check if user exists
    if user.username in users_db:
        logger.warning(f"User already exists: {user.username}")
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    new_user = User(
        id=len(users_db) + 1,
        username=user.username,
        email=user.email
    )
    users_db[user.username] = new_user
    logger.info(f"User registered: {user.username}")
    return new_user


@app.post("/login", tags=["Auth"])
def login(credentials: UserLogin):
    """Login user and get token"""
    logger.info(f"Login attempt for user: {credentials.username}")
    
    # Check if user exists
    user = users_db.get(credentials.username)
    if user is None:
        logger.warning(f"User not found: {credentials.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token({"sub": user.username})
    logger.info(f"Login successful for user: {credentials.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================
# ✅ PART 7: ROOT ENDPOINT
# ============================================

@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API info"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Blog Platform FastAPI",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login",
            "create_post": "POST /posts/",
            "get_all_posts": "GET /posts/",
            "get_post": "GET /posts/{post_id}",
            "update_post": "PUT /posts/{post_id}",
            "delete_post": "DELETE /posts/{post_id}",
            "create_comment": "POST /posts/{post_id}/comments",
            "get_comments": "GET /posts/{post_id}/comments",
            "delete_comment": "DELETE /posts/{post_id}/comments/{comment_id}"
        }
    }


# ============================================
# ✅ PART 8: POST ENDPOINTS
# ============================================

@app.post("/posts/", response_model=Post, status_code=status.HTTP_201_CREATED, tags=["Posts"])
def create_post(post: PostCreate, current_user: User = Depends(get_current_user)):
    """Create new blog post"""
    global next_post_id
    logger.info(f"Creating post by user: {current_user.username}")
    
    new_post = Post(
        id=next_post_id,
        title=post.title,
        content=post.content,
        author_id=current_user.id,
        created_at=datetime.utcnow()
    )
    
    posts_db[next_post_id] = new_post
    next_post_id += 1
    
    logger.info(f"Post created with ID: {new_post.id}")
    return new_post


@app.get("/posts/", response_model=List[Post], status_code=status.HTTP_200_OK, tags=["Posts"])
def get_all_posts(current_user: User = Depends(get_current_user)):
    """Get all blog posts"""
    logger.info(f"Fetching all posts for user: {current_user.username}")
    
    posts = list(posts_db.values())
    logger.debug(f"Found {len(posts)} posts")
    return posts


@app.get("/posts/{post_id}", response_model=Post, status_code=status.HTTP_200_OK, tags=["Posts"])
def get_post(post_id: int, current_user: User = Depends(get_current_user)):
    """Get specific blog post"""
    logger.info(f"Fetching post {post_id} for user: {current_user.username}")
    
    post = posts_db.get(post_id)
    if post is None:
        logger.warning(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    logger.debug(f"Post found: {post.title}")
    return post


@app.put("/posts/{post_id}", response_model=Post, status_code=status.HTTP_200_OK, tags=["Posts"])
def update_post(post_id: int, post_update: PostUpdate, current_user: User = Depends(get_current_user)):
    """Update blog post"""
    logger.info(f"Updating post {post_id} by user: {current_user.username}")
    
    post = posts_db.get(post_id)
    if post is None:
        logger.warning(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is author
    if post.author_id != current_user.id:
        logger.warning(f"User {current_user.username} tried to update post by another user")
        raise HTTPException(status_code=403, detail="Cannot update post by another user")
    
    # Update only provided fields
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content
    
    logger.info(f"Post {post_id} updated")
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Posts"])
def delete_post(post_id: int, current_user: User = Depends(get_current_user)):
    """Delete blog post"""
    logger.info(f"Deleting post {post_id} by user: {current_user.username}")
    
    post = posts_db.get(post_id)
    if post is None:
        logger.warning(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is author
    if post.author_id != current_user.id:
        logger.warning(f"User {current_user.username} tried to delete post by another user")
        raise HTTPException(status_code=403, detail="Cannot delete post by another user")
    
    del posts_db[post_id]
    logger.info(f"Post {post_id} deleted")
    return None


# ============================================
# ✅ PART 9: COMMENT ENDPOINTS
# ============================================

@app.post("/posts/{post_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED, tags=["Comments"])
def create_comment(post_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user)):
    """Create comment on blog post"""
    global next_comment_id
    logger.info(f"Creating comment on post {post_id} by user: {current_user.username}")
    
    # Check if post exists
    post = posts_db.get(post_id)
    if post is None:
        logger.warning(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = Comment(
        id=next_comment_id,
        content=comment.content,
        post_id=post_id,
        author_id=current_user.id,
        created_at=datetime.utcnow()
    )
    
    if post_id not in comments_db:
        comments_db[post_id] = []
    
    comments_db[post_id].append(new_comment)
    next_comment_id += 1
    
    logger.info(f"Comment created with ID: {new_comment.id}")
    return new_comment


@app.get("/posts/{post_id}/comments", response_model=List[Comment], status_code=status.HTTP_200_OK, tags=["Comments"])
def get_comments(post_id: int, current_user: User = Depends(get_current_user)):
    """Get all comments on blog post"""
    logger.info(f"Fetching comments for post {post_id} by user: {current_user.username}")
    
    # Check if post exists
    post = posts_db.get(post_id)
    if post is None:
        logger.warning(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_comments = comments_db.get(post_id, [])
    logger.debug(f"Found {len(post_comments)} comments for post {post_id}")
    return post_comments


@app.delete("/posts/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Comments"])
def delete_comment(post_id: int, comment_id: int, current_user: User = Depends(get_current_user)):
    """Delete comment on blog post"""
    logger.info(f"Deleting comment {comment_id} from post {post_id} by user: {current_user.username}")
    
    # Check if post exists
    if post_id not in comments_db:
        logger.warning(f"Post not found: {post_id}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Find comment
    post_comments = comments_db[post_id]
    comment = None
    for c in post_comments:
        if c.id == comment_id:
            comment = c
            break
    
    if comment is None:
        logger.warning(f"Comment not found: {comment_id}")
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user is author
    if comment.author_id != current_user.id:
        logger.warning(f"User {current_user.username} tried to delete comment by another user")
        raise HTTPException(status_code=403, detail="Cannot delete comment by another user")
    
    post_comments.remove(comment)
    logger.info(f"Comment {comment_id} deleted")
    return None


# ============================================
# ✅ PART 10: RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
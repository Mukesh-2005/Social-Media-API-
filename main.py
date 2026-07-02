# main.py
from fastapi import FastAPI
from database import engine, Base
from models import UserModel, PostModel, CommentModel, LikeModel, FollowModel
from routers import users, posts, comments, follows, feeds 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

# Create FastAPI app
app = FastAPI(
    title="Social Media API",
    version="1.0.0",
    description="Twitter-like Social Media API"
)

# Include routers
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(follows.router)
app.include_router(feeds.router) 

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """API documentation"""
    return {
        "message": "Social Media API (Twitter-like)",
        "database": "MySQL",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)
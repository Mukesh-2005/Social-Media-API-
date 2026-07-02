# seed_data.py
import os
import random
from datetime import datetime, timedelta
from faker import Faker
from database import SessionLocal, engine, Base
from models import UserModel, PostModel, CommentModel, LikeModel, FollowModel

fake = Faker()
db = SessionLocal()

def clear_database():
    # Clear all data from tables
    print(" Clearing database...")
    db.query(LikeModel).delete()
    db.query(CommentModel).delete()
    db.query(FollowModel).delete()
    db.query(PostModel).delete()
    db.query(UserModel).delete()
    db.commit()
    print(" Database cleared")


def create_users(count=100):
    """Create fake users"""
    print(f" Creating {count} users...")
    users = []
    
    for i in range(count):
        user = UserModel(
            username=f"user_{fake.user_name()}_{i}",
            email=f"user{i}@example.com",
            password_hash=fake.password(),
            bio=fake.sentence(),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
            followers_count=random.randint(0, 500),
            following_count=random.randint(0, 500)
        )
        users.append(user)
    
    db.add_all(users)
    db.commit()
    print(f" Created {count} users")
    return users


def create_posts(users, count=500):
    """Create fake posts"""
    print(f"Creating {count} posts...")
    posts = []
    
    for i in range(count):
        user = random.choice(users)
        post = PostModel(
            content=fake.sentence(nb_words=20),
            user_id=user.id,
            likes_count=random.randint(0, 1000),
            comments_count=random.randint(0, 100),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
        )
        posts.append(post)
    
    db.add_all(posts)
    db.commit()
    print(f"Created {count} posts")
    return posts


def create_comments(users, posts, count=1000):
    """Create fake comments"""
    print(f" Creating {count} comments...")
    comments = []
    
    for i in range(count):
        user = random.choice(users)
        post = random.choice(posts)
        comment = CommentModel(
            content=fake.sentence(nb_words=10),
            post_id=post.id,
            user_id=user.id,
            likes_count=random.randint(0, 100),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
        )
        comments.append(comment)
        # Update post's comment count
        post.comments_count += 1
    
    db.add_all(comments)
    db.commit()
    print(f" Created {count} comments")
    return comments


def create_likes(users, posts, count=1000):
    """Create fake likes"""
    print(f" Creating {count} likes...")
    likes = []
    created_count = 0
    
    for i in range(count):
        user = random.choice(users)
        post = random.choice(posts)
        
        # Check if already liked
        existing = db.query(LikeModel).filter(
            LikeModel.user_id == user.id,
            LikeModel.post_id == post.id
        ).first()
        
        if not existing:
            like = LikeModel(
                user_id=user.id,
                post_id=post.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            likes.append(like)
            post.likes_count += 1
            created_count += 1
    
    db.add_all(likes)
    db.commit()
    print(f"Created {created_count} likes")


def create_follows(users, count=500):
    """Create follow relationships"""
    print(f" Creating {count} follow relationships...")
    follows = []
    created_count = 0
    
    for i in range(count):
        follower = random.choice(users)
        following = random.choice(users)
        
        # Don't follow yourself
        if follower.id == following.id:
            continue
        
        # Check if already following
        existing = db.query(FollowModel).filter(
            FollowModel.follower_id == follower.id,
            FollowModel.following_id == following.id
        ).first()
        
        if not existing:
            follow = FollowModel(
                follower_id=follower.id,
                following_id=following.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            follows.append(follow)
            follower.following_count += 1
            following.followers_count += 1
            created_count += 1
    
    db.add_all(follows)
    db.commit()
    print(f"Created {created_count} follow relationships")


def run_seeding():
    """Run all seeding"""
    print("\n" + "="*50)
    print("🌱 STARTING DATABASE SEEDING")
    print("="*50 + "\n")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print(" Tables created/verified\n")
        
        # Clear existing data
        clear_database()
        print()
        
        # Create data
        users = create_users(100)
        print()
        
        posts = create_posts(users, 500)
        print()
        
        create_comments(users, posts, 1000)
        print()
        
        create_likes(users, posts, 1000)
        print()
        
        create_follows(users, 500)
        print()
        
        print("="*50)
        print(" SEEDING COMPLETE!")
        print("="*50)
        print("\nDatabase Statistics:")
        print(f"  Users: {db.query(UserModel).count()}")
        print(f"  Posts: {db.query(PostModel).count()}")
        print(f"  Comments: {db.query(CommentModel).count()}")
        print(f"  Likes: {db.query(LikeModel).count()}")
        print(f"  Follows: {db.query(FollowModel).count()}")
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run_seeding()
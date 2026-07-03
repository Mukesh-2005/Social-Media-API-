# 🚀 Social Media API (Twitter-like)

A full-featured REST API for a Twitter-like social media platform built with **FastAPI** and **MySQL**.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Author](#author)

---

## ✨ Features

✅ **User Management**
- User registration and authentication
- User profiles with bio
- Follow/unfollow users
- Follower statistics

✅ **Posts**
- Create, read, update, delete posts
- Like/unlike posts
- Like counter

✅ **Comments**
- Comment on posts
- Like/unlike comments
- Comment management

✅ **Feeds**
- Personalized user feed (from followed users)
- Trending posts (by likes)
- Recent posts
- Most commented posts
- User timeline
- Explore/discover feed
- Mutual friends feed
- User engagement statistics

✅ **Analytics**
- Post performance metrics
- User engagement tracking
- Trending users and posts
- Feed statistics

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI |
| Database | MySQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Server | Uvicorn |
| Python Version | 3.8+ |

---

## 📁 Project Structure

```
social_media_api/
├── main.py                 # Main FastAPI app
├── database.py             # Database configuration
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── routers/
│   ├── init.py
│   ├── users.py            # User endpoints (5)
│   ├── posts.py            # Post endpoints (10)
│   ├── comments.py         # Comment endpoints (11)
│   ├── follows.py          # Follow endpoints (9)
│   └── feeds.py            # Feed endpoints (10)
├── requirements.txt        # Python dependencies
└── README.md              # This file
``` 
---

## ⚙️ Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- XAMPP (for local MySQL)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/Mukesh-2005/social_media_api.git
cd social_media_api
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start MySQL (XAMPP)**
Open XAMPP Control Panel
Click "Start" for MySQL

5. **Run the API**
```bash
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --port 8003
```

6. **Access the API**
- API Documentation: http://127.0.0.1:8003/docs
- Alternative Docs: http://127.0.0.1:8003
- **Live Demo:** https://social-media-api-ispt.onrender.com/docs

---


## 🔌 API Endpoints

### Users (5 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create new user |
| GET | `/users/{user_id}` | Get user by ID |
| GET | `/users` | List all users |
| PUT | `/users/{user_id}` | Update user profile |
| DELETE | `/users/{user_id}` | Delete user |

### Posts (10 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/posts` | Create post |
| GET | `/posts/{post_id}` | Get single post |
| GET | `/posts` | Get all posts |
| GET | `/posts/user/{user_id}` | Get user's posts |
| PUT | `/posts/{post_id}` | Update post |
| DELETE | `/posts/{post_id}` | Delete post |
| POST | `/posts/{post_id}/like` | Like post |
| DELETE | `/posts/{post_id}/like` | Unlike post |
| GET | `/posts/{post_id}/likes-count` | Get likes count |
| GET | `/posts/{post_id}/detailed` | Get post with author |

### Comments (11 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/comments` | Create comment |
| GET | `/comments/{comment_id}` | Get single comment |
| GET | `/comments` | Get all comments |
| GET | `/comments/post/{post_id}` | Get post comments |
| GET | `/comments/user/{user_id}` | Get user's comments |
| PUT | `/comments/{comment_id}` | Update comment |
| DELETE | `/comments/{comment_id}` | Delete comment |
| POST | `/comments/{comment_id}/like` | Like comment |
| DELETE | `/comments/{comment_id}/like` | Unlike comment |
| GET | `/comments/{comment_id}/likes-count` | Get likes count |
| GET | `/comments/{comment_id}/detailed` | Get comment with details |

### Follows (9 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/follows` | Follow user |
| DELETE | `/follows` | Unfollow user |
| GET | `/follows/{user_id}/followers` | Get followers |
| GET | `/follows/{user_id}/following` | Get following |
| GET | `/follows/check` | Check if following |
| GET | `/follows/{user_id}/followers-count` | Get followers count |
| GET | `/follows/{user_id}/following-count` | Get following count |
| GET | `/follows/mutual/{user_id1}/{user_id2}` | Get mutual followers |
| GET | `/follows/{user_id}/stats` | Get follow stats |

### Feeds (10 endpoints)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/feeds/{user_id}` | Personalized feed |
| GET | `/feeds/{user_id}/timeline` | User's posts |
| GET | `/feeds/trending/posts` | Trending posts |
| GET | `/feeds/recent/posts` | Recent posts |
| GET | `/feeds/most-commented/posts` | Most commented |
| GET | `/feeds/{user_id}/liked-posts` | User's liked posts |
| GET | `/feeds/trending/users` | Trending users |
| GET | `/feeds/{user_id}/stats` | User statistics |
| GET | `/feeds/mutual-feed/{user_id1}/{user_id2}` | Mutual friends feed |
| GET | `/feeds/explore/posts` | Explore posts |

---

## 🗄️ Database Schema

### Tables
- **users** - User accounts
- **posts** - User posts/tweets
- **comments** - Comments on posts
- **likes** - Likes on posts
- **follows** - Follow relationships

### Relationships
```
users ----1:N---- posts
users ----1:N---- comments
users ----1:N---- likes
users ----M:N---- follows (self-referential)
posts ----1:N---- comments
posts ----1:N---- likes
```
---

## 💡 Key Features Explained

### Personalized Feed
- Shows posts from users you follow
- Ordered by newest first
- Pagination support

### Trending
- Posts sorted by likes count
- Users sorted by followers count
- Most commented posts

### Engagement Metrics
- Like counts on posts and comments
- Comment counts on posts
- Follower/following statistics
- User engagement statistics

---

## 🔐 Security Notes

⚠️ **Current Implementation:**
- Passwords stored as plain text (for learning)
- No JWT authentication yet
- No rate limiting

✅ **For Production, Add:**
- Password hashing (bcrypt)
- JWT tokens
- Rate limiting
- Input validation
- CORS configuration
- HTTPS only

---

## 📊 Sample Data

### Quick Test
1. Create 3 users
2. Have them follow each other
3. Create posts from each user
4. Like and comment on posts
5. View personalized feeds

---

## 🚀 Future Enhancements

- [ ] User authentication (JWT)
- [ ] Password hashing
- [ ] Rate limiting
- [ ] User search
- [ ] Hashtags support
- [ ] Direct messaging
- [ ] Notifications
- [ ] Image uploads
- [ ] User blocking
- [ ] Report/moderation

---

## 📈 Performance Considerations

- Database indexes on foreign keys
- Pagination for all list endpoints
- Efficient JOINs for feed queries
- Aggregation queries for statistics

---

## 🧪 Testing

Test endpoints using:
- Swagger UI: http://127.0.0.1:8003/docs
- ReDoc: http://127.0.0.1:8003/redoc
- Postman (import from Swagger)
- cURL (see Usage section)

---

## 📝 Learning Outcomes

This project demonstrates:
✅ FastAPI best practices
✅ SQLAlchemy ORM
✅ Database design
✅ REST API principles
✅ Complex SQL queries
✅ Project structure
✅ Pagination and filtering
✅ Error handling

---

## 👨‍💻 Author

**Mukesh K**
- GitHub: [@Mukesh-2005](https://github.com/Mukesh-2005)
- Email: starmukesh2005@gmail.com
- LinkedIn: [Mukesh K](https://www.linkedin.com/in/mukesh-k-5a9a5b/)

---

## 📜 License

MIT License - Feel free to use this project for learning!

---

## 🙏 Acknowledgments

- Built as part of 8-month data science learning journey
- FastAPI documentation
- SQLAlchemy documentation
- Community support

---

## 📞 Support

For questions or issues:
1. Check API documentation at `/docs`
2. Review code comments
3. Open GitHub issues
4. Contact author

---

**Happy coding! 🚀**

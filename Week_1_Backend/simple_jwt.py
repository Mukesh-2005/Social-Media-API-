#step 1 importing libraries 

from datetime import datetime, timedelta
import jwt 
import logging
#step 2 setting up logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#step 2 : Configuration
SECRET_KEY = "your_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger.info("Configuration loaded")
logger.debug(f"SECRET_KEY: {SECRET_KEY}")
logger.debug(f"ALGORITHM: {ALGORITHM}")
logger.debug(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")

#step 3 : Function to create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    logger.debug(f"Data to encode: {to_encode}")
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.debug(f"Token expiration time: {expire}")
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)    
    logger.debug(f"Encoded JWT: {encoded_jwt[:50]}...")  # Log only the first 50 characters for security
    return encoded_jwt

if __name__ == "__main__":
    token = create_access_token({"sub": "Mukesh"})
    print(f"Generated JWT: {token}")

def verify_access_token(token: str):
    try:
        logger.debug(f"Verifying token: {token[:50]}...")  # Log only the first 50 characters for security
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Token verified")

        username = payload.get("sub")
        logger.debug(f"Username extracted from token: {username}")

        exp_time = payload.get("exp")
        logger.debug(f"Token expiration time from payload: {datetime.utcfromtimestamp(exp_time)}")
        return username
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return None
    
if __name__ == "__main__":
    token = create_access_token({"sub": "Mukesh"})
    print(f"Generated JWT: {token}")
    username = verify_access_token(token)
    print(f"Verified username: {username}")

    print("/n--- Test 2: Verifiy with wrong secret key ---")
    wrong_secret = "wrong_secret_key"
    try:
        payload = jwt.decode(token, wrong_secret, algorithms=[ALGORITHM])
        print(f"Token verified with wrong secret key: {payload}")
    except jwt.InvalidTokenError:
        print("Invalid token with wrong secret key")    
    
    print("/n--- Test 3: Verifiy with expired token --- ")
    tampered = token[:-5] + "abcde"  # Tampering the token to simulate expiration
    username = verify_access_token(tampered)
    print(f"Verified username with tampered token: {username}")

#step 5: Simulate Login 
def login(username: str, password: str):

    logger.info(f"Attempting login for user: {username}")

    if len(username) < 1 or len(password) < 1:
        logger.warning("Username or password is empty")
        return None
    logger.debug(f"password varified")
    logger.debug(f"Creating access token for user: {username}")
    token = create_access_token({"sub": username})
    logger.info(f"Access token created for user: {username}")
    return token

if __name__ == "__main__":
    print("\n\n========== COMPLETE JWT FLOW ==========\n")
    
    # Step 1: Login
    print("Step 1: LOGIN")
    token = login("Mukesh", "password123")
    print(f"Token: {token}\n")
    
    # Step 2: Use token
    print("Step 2: VERIFY TOKEN")
    username = verify_access_token(token)
    print(f"Verified as: {username}\n")
    
    # Step 3: Try with wrong token
    print("Step 3: REJECT WRONG TOKEN")
    bad_token = "invalid.token.here"
    username = verify_access_token(bad_token)
    print(f"Result: {username}\n")
    
    print("========== FLOW COMPLETE ==========\n")

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # Refresh token valid for 7 days
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            logger.error("Invalid token type")
            return None
        username = payload.get("sub")
        logger.debug(f"Username extracted from refresh token: {username}")
        return username
    except jwt.ExpiredSignatureError:
        logger.error("Refresh token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid refresh token")
        return None

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            logger.error("Invalid token type")
            return None
        username = payload.get("sub")
        logger.debug(f"Username extracted from refresh token: {username}")
        return username
    except jwt.ExpiredSignatureError:
        logger.error("Refresh token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid refresh token")
        return None

def refresh_access_token(refresh_token: str):
    username = verify_refresh_token(refresh_token)
    if username:
        logger.info(f"Refreshing access token for user: {username}")
        new_access_token = create_access_token({"sub": username})
        logger.info(f"New access token created for user: {username}")
        return new_access_token
    else:
        logger.error("Failed to refresh access token due to invalid refresh token")
        return None
    new_access_token = create_access_token({"sub": username})
    logger.info(f"New access token created for user: {username}")  
    return new_access_token

if __name__ == "__main__":
    print("\n\n========== COMPLETE REFRESH TOKEN FLOW ==========\n")
    
    # Step 1: Login - Get both tokens
    print("Step 1: LOGIN (Get access + refresh tokens)")
    access_token = create_access_token({"sub": "Mukesh"})
    refresh_token = create_refresh_token({"sub": "Mukesh"})
    print(f"Access token:  {access_token[:50]}...")
    print(f"Refresh token: {refresh_token[:50]}...\n")
    
    # Step 2: Use access token
    print("Step 2: USE ACCESS TOKEN")
    username = verify_access_token(access_token)
    print(f"Access token valid for: {username}\n")
    
    # Step 3: Simulate token expiration
    print("Step 3: ACCESS TOKEN EXPIRED (wait 30 min)")
    print("(Simulating: time passed, access token expired)\n")
    
    # Step 4: Refresh token
    print("Step 4: REFRESH TOKEN (Get new access token)")
    new_access_token = refresh_access_token(refresh_token)
    print(f"New access token: {new_access_token[:50]}...\n")
    
    # Step 5: Use new access token
    print("Step 5: USE NEW ACCESS TOKEN")
    username = verify_access_token(new_access_token)
    print(f"New access token valid for: {username}\n")
    
    # Step 6: Verify refresh token still works
    print("Step 6: VERIFY REFRESH TOKEN STILL WORKS")
    is_valid = verify_refresh_token(refresh_token)
    print(f"Refresh token still valid: {is_valid is not None}\n")
    
   # Replace Step 7 in simple_jwt.py with
    print("Step 7: TRY ACTUALLY EXPIRED TOKEN")
    past_time = datetime.utcnow() - timedelta(minutes=1)
    expired_payload = {"sub": "Mukesh", "exp": past_time}
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    username = verify_access_token(expired_token)
    print(f"Result: {username} (should be None)\n")
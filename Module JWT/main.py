from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import jwt
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHAM = os.getenv("ALGORITHAM")
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client = AsyncIOMotorClient(MONGO_URI)
user_collection = client.GAIDB.users

class User(BaseModel):
  username: str
  password: str
  

def create_access_token(data: dict):
  return jwt.encode({**data, "exp": datetime.utcnow()+ timedelta(minutes=30)}, SECRET_KEY, algorithm=ALGORITHAM)

def get_current_user(token: str = Header(...)):
  try:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHAM])["username"]
  except Exception:
    raise HTTPException(status_code=404, detail={"message": "Token Invalid or Expired"})
  
@app.post("/signup")
async def signup(user: User):
  if await user_collection.find_one({"username": user.username}):
    raise HTTPException(status_code=400, detail={"message": "User already exist"})
  
  hashed_password = pwd_context.hash(user.password)
  await user_collection.insert_one({"username": user.username, "password": hashed_password})
  return JSONResponse(status_code=400, content={"message": "User resistered"})

@app.post("/signin")
async def signin(user: User):
  db_user = await user_collection.find_one({"username": user.username})
  if not db_user or not pwd_context.verify(user.password, db_user["password"]):
    raise HTTPException(status_code=401, detail={"message": "User does not exist"})
  
  token = create_access_token({"username": user.username})
  return JSONResponse(status_code=200, content={"access_token": token})


@app.get("/protected")
async def protected(username: str = Depends(get_current_user)):
  return JSONResponse(status_code=200, content={"message": f"Hii {username}, welcome"})


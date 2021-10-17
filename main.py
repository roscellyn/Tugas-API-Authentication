import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

with open("menu.json", "r") as read_file:
    data = json.load(read_file)

SECRET_KEY = "45e307f4d0fd7b020eae6d29c230afdabe4e5414f47ab3d1f553e92158201d9f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title='UTS II3160 - API Authentication',
    description='by Jacelyn Felisha 18219097\n\nHow to use:\n1. Click Authorize then input username and password\n2. Access Token will automatically be created and expired in 30min\n3. Now you can modify the menu!')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

fake_users_db = {
    "asdf": {
        "username": "asdf",
        "hashed_password": "$2b$12$ZJ1vwWXC28QP26XfR2PC9O.rElXP0G1Jbtq4s0kwLL7OwE/4JO7b6",
    },
}

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token, tags=["user authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", tags=["user authentication"])
async def read_my_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.get('/')
def root():
    return{'Menu':'Item'}

@app.get('/menu/{item_id}', tags=["menu"])
async def read_menu(item_id: int, current_user: User = Depends(get_current_user)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )

@app.get('/menu', tags=["menu"])
async def read_all_menu(current_user: User = Depends(get_current_user)):
    return data['menu']
    raise HTTPException(
        status_code=404, detail=f'Data not found'
        )

@app.post('/menu', tags=["menu"])
async def add_menu(name: str, current_user: User = Depends(get_current_user)):
    id=1
    if(len(data['menu'])>0):
        id=data['menu'][len(data['menu'])-1]['id']+1
    new_menu = {
        "id": id,
        "name": name
    }
    data['menu'].append(dict(new_menu))
    read_file.close()
    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
    write_file.close()    

    return new_menu
    raise HTTPException(
        status_code=500, detail=f'Internal server error'
        )

@app.put('/menu',  tags=["menu"])
async def update_menu(item_id: int , name: str, current_user: User = Depends(get_current_user) ):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            menu_item['name'] = name
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()

    return({"message": "Menu updated successfully"})
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )

@app.delete('/menu', tags=["menu"])
async def delete_menu(item_id: int, current_user: User = Depends(get_current_user) ):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()

    return({"message": "Item deleted successfully"})
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )
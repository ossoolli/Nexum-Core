from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import time

app = FastAPI(
    title="{APP_NAME}",
    description="{APP_DESCRIPTION}",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# Mock Database
db = []

@app.get("/")
async def root():
    return {"message": "Welcome to {APP_NAME} API", "status": "online", "timestamp": time.time()}

@app.get("/items", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    return db[skip : skip + limit]

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    item.id = len(db) + 1
    db.append(item)
    return item

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

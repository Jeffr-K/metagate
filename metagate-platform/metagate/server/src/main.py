import uvicorn
from src.bootstrap import Bootstrap

app = Bootstrap().instance

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
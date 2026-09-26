from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Mera AI 3D Server Live Hai!"}

from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Success", "message": "SecureCivic Backend is Running!"}
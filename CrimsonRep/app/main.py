import uvicorn
from fastapi import FastAPI

app = FastAPI(title= "CrimsonRep API")

@app.get("/")
async def root():
    return {"message" : "CrimsonRep API is running"}

if __name__ in "__main__":
    uvicorn.run("CrimsonRep.app.main:app",
                host= "0.0.0.0",
                port= 8000,
                reload= True)
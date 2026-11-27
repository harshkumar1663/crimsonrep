import uvicorn
from fastapi import FastAPI
from CrimsonRep.apis.auth import router as auth_router
from CrimsonRep.apis.exercises import router as exercise_router
from CrimsonRep.apis.sessions import router as session_router

app = FastAPI(title= "CrimsonRep API")

app.include_router(auth_router, prefix="/auth")
app.include_router(exercise_router)
app.include_router(session_router)

@app.get("/")
async def root():
    return {"message" : "CrimsonRep API is running"}

if __name__ in "__main__":
    uvicorn.run("CrimsonRep.app.main:app",
                host= "0.0.0.0",
                port= 8000,
                reload= True)
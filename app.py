from fastapi import FastAPI
from controllers.conversation_controller import router as conversation_router
from controllers.missing_info_controller import router as missing_info_router
from controllers.greeting_controller import router as greeting_router

app = FastAPI()

# Include routers
app.include_router(conversation_router)
app.include_router(missing_info_router)
app.include_router(greeting_router)

if __name__ == "__main__":
    import uvicorn
    from config import Config
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
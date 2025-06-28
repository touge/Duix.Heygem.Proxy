# main.py
from proxy_service.config import create_app
from proxy_service.routers.generate import router as gen_router
from proxy_service.routers.progress import router as prog_router
from proxy_service.routers.characters import router as char_router
from settings import settings

app = create_app()
app.include_router(gen_router)
app.include_router(prog_router)
app.include_router(char_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )

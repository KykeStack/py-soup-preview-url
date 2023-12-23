from fastapi import FastAPI, Request, HTTPException, status, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
import uvicorn

from core.config import settings
from modules.url_preview import get_url_preview
from core.deps import get_access

app = FastAPI(
    title=settings.PROJECT_NAME, 
    swagger_ui_parameters={"tryItOutEnabled": True}
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/", tags=['Documentation'])
async def docs():
    return RedirectResponse(app.docs_url)

@app.get("/url", tags=['UrlPreview'])
async def url_preview(url: str, access = Depends(get_access)):
    if not access.status:
        print(access.error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    try: 
        data = await get_url_preview(url)
        return {
            "data": data
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not get url preview, check if your URL is valid"
        )

@app.get("/heartbeat", tags=["heartbeat"])
async def heartbeat(req: Request):
    return { "baseUrl": req.base_url}

if settings.DEV_MODE:
    from core.security import create_access_token_dev
    
    @app.get("/token", tags=['GetToken'])
    async def generate_jwt():
        return {
            "token": create_access_token_dev(subject="http://localhost:3000/")
        }

if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True)
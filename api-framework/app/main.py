from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.routes import base, auth
from app.middleware.error_handler import ErrorHandlingMiddleware

app = FastAPI(title="Backend API Framework")

# Middleware
app.add_middleware(ErrorHandlingMiddleware)

# Routers
app.include_router(base.router)
app.include_router(auth.router)

# Static directory (for custom CSS/JS)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# ✅ Custom Swagger Docs
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Backend API Framework",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    ).replace(
        "</head>",
        '<link rel="stylesheet" type="text/css" href="/static/custom-swagger.css"></head>'
    )


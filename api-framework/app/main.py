from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

# Routers & middleware
from app.routes import base, auth, cache_demo, process_image
from app.middleware.error_handler import ErrorHandlingMiddleware

# 1) Create the app FIRST
app = FastAPI(
    title="Backend API Framework",
    default_response_class=ORJSONResponse,
    # leave defaults so FastAPI serves its own Swagger assets
    docs_url="/docs",
    redoc_url="/redoc",
)

# 2) Middleware
from app.routes import stock  
from app.routes import base, auth, cache_demo, process_image

# 3) Routers (now 'app' exists, so this is safe)
app.include_router(cache_demo.router, prefix="/api")
app.include_router(stock.router, prefix="/api")  
app.include_router(process_image.router, prefix="/api")
app.include_router(base.router)
app.include_router(auth.router)

# 4) Static directory (keep your existing code)
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

#Serve the dashboard HTML
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    html_path = BASE_DIR / "static" / "dashboard" / "index.html"
    return html_path.read_text(encoding="utf-8")

# 5) (Optional) Custom Swagger docs (keep your existing function if you have one)
# @app.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html():
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title="Backend API Framework",
#         swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js",
#         swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css",
#     )

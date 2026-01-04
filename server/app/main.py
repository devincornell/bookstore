from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
#from app.api.endpoints.books import router as books_router


from app.core.config import app_settings
from app.api.endpoints.book_research import router as research_router
from app.api.endpoints.extract import router as extract_router

# Create FastAPI instance
app = FastAPI(
    title="Bookstore API",
    description="A FastAPI application for managing a bookstore with SQLAlchemy ORM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure templates
templates = Jinja2Templates(directory="templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
#app.include_router(
#    books_router, 
#    prefix="/books", 
#    tags=["books"]
#)

app.include_router(
    research_router,
    prefix="/research",
    tags=["book-research"]
)

app.include_router(
    extract_router,
    prefix="/extract",
    tags=["book-extract"]
)

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Bookstore API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/bookstore", response_class=HTMLResponse)
async def bookstore_frontend(request: Request):
    """Serve the bookstore frontend HTML page"""
    return templates.TemplateResponse("bookstore.html", {"request": request})

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.DEBUG
    )
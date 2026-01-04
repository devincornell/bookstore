from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from app.api.endpoints.books import router as books_router
from app.api.endpoints.book_research import router as research_router  # Re-enabled with google-genai
from app.core.config import app_settings

# Create FastAPI instance
app = FastAPI(
    title="Bookstore API",
    description="A FastAPI application for managing a bookstore with SQLAlchemy ORM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Bookstore API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

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
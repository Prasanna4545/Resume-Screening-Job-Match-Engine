from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import get_settings
from app.database import engine, Base, get_db
from app.api import jobs_router, resumes_router, matching_router
from app.services.embedding_service import get_embedding_model
from app.services.resume_parser import get_nlp
import app.models  # Ensure models are imported for table creation

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load ML and NLP models once at application startup
    try:
        get_nlp()
        get_embedding_model()
    except Exception as e:
        print(f"Warning during startup model pre-loading: {e}")
    yield

# Create tables automatically if DB exists
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning during table creation on startup: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
allowed_origins_set = {origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()}
if settings.FRONTEND_URL:
    allowed_origins_set.add(settings.FRONTEND_URL.strip())
origins = list(allowed_origins_set)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(jobs_router, prefix="/api")
app.include_router(resumes_router, prefix="/api")
app.include_router(matching_router, prefix="/api")

@app.get("/health")
def root_health():
    """Root health check endpoint for Render health checks."""
    return {"status": "ok"}

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }

@app.get("/api/db-health")
def db_health_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {
                "status": "ok",
                "database": "connected",
                "result": result
            }
        else:
            raise HTTPException(status_code=500, detail="Unexpected database query result")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


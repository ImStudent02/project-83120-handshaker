from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.mongodb import connect_db, close_db
from app.routes import auth, users, signaling, connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Project 83120 - Handshaker",
    description="""
    P2P Secure Chat Signaling Server.
    
    **Server Role:**
    - User authentication
    - User discovery (public keys)
    - Connection request management
    - WebRTC signaling relay (encrypted blobs only)
    
    **Server Does NOT:**
    - Store messages or files
    - Decrypt any payload
    - Have access to private keys
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(connection.router)
app.include_router(signaling.router)


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "handshaker"}


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "service": "Project 83120 - Handshaker",
        "docs": "/docs",
        "health": "/health",
    }

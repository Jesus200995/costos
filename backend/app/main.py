from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, catalogos
from app.config import settings

app = FastAPI(title="COSTOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "https://costos.sembrandodatos.com",
        "https://apicostos.sembrandodatos.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(catalogos.router, prefix="/api/catalogos", tags=["catalogos"])


@app.get("/api/health")
def health():
    from datetime import datetime, timezone
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

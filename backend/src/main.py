from fastapi import FastAPI
from .api.auth_routes import router as auth_router
from .api.vault_routes import router as vault_router
from .api.admin_routes import router as admin_router

app = FastAPI(title="SecureVault API", version="1.0.0")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(vault_router, prefix="/vault", tags=["vault"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SecureVault API"}
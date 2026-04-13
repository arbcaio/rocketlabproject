from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import consumidor as consumidor_router
from app.routers import pedido as pedido_router
from app.routers import produto as produto_router
from app.routers import vendedor as vendedor_router

app = FastAPI(
    title="Sistema de Gerenciamento de E-Commerce",
    description="API para gerenciamento de produtos, vendas e avaliações.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(produto_router.router)
app.include_router(consumidor_router.router)
app.include_router(vendedor_router.router)
app.include_router(pedido_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "API rodando com sucesso!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

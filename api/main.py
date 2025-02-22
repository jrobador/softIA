from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from data_generation.finetune_rag import router as finetune_router

app = FastAPI(
    title="API - SoftIA",
    description="API para entrenar e implementar modelos LLaMA optimizados",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(finetune_router, prefix="/finetuning-rag", tags=["fine-tuning"])

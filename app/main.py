from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import router as api_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Moteur d'Intelligence Artificielle pour Digital School. "
        "Intègre la détection du décrochage, l'orientation prédictive, "
        "l'assistance vocale et la génération de contenus pédagogiques via Groq/LLM."
    ),
    docs_url="/docs",  
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    api_router, 
    prefix=settings.API_V1_STR,
    tags=["Services IA Appliquée"]
)


@app.get("/", tags=["Système"])
async def root():
    """
    Vérification rapide de la disponibilité du service.
    Utile pour les tests de connectivité initiaux.
    """
    return {
        "project": settings.PROJECT_NAME,
        "message": "Le moteur IA de Digital School est opérationnel.",
        "status": "active",
        "version": settings.VERSION
    }

@app.get("/health", tags=["Système"])
async def health_check():
    """
    Endpoint de diagnostic (Health Check).
    Utilisé par AWS Elastic Beanstalk ou ECS pour surveiller l'état du conteneur.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "infrastructure": "AWS Ready",
        "llm_provider": "Groq (LPU Inference Engine Engine)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
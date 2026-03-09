from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    QuizRequest, 
    QuizResponse, 
    SummaryRequest, 
    SummaryResponse,
    AudioRequest,
    AudioResponse,
    DropoutAnalysisRequest, RiskIndicator,
    AdmissionRequest, AdmissionResponse
)
from app.services.llm_service import llm_service
from app.services.audio_service import audio_service
from app.services.ml_service import ml_service


router = APIRouter()

@router.post(
    "/generate-quiz", 
    response_model=QuizResponse,
    status_code=status.HTTP_200_OK,
    summary="Générer un quiz ou devoir",
    description="Exploite le LLM pour créer des contenus structurés et éditables basés sur les cours[cite: 53, 56]."
)
async def create_quiz(request: QuizRequest):
    """
    Endpoint pour la génération dynamique de quiz, exercices ou devoirs.
    Prend en charge le contexte documentaire (RAG) pour limiter l'IA aux cours réels[cite: 54].
    """
    try:
        return await llm_service.generate_quiz(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erreur lors de la génération du contenu : {str(e)}"
        )



@router.post(
    "/generate-summary", 
    response_model=SummaryResponse,
    summary="Générer des commentaires de bulletin",
    description="Automatise la production de résumés analytiques à partir des notes et absences[cite: 59, 60]."
)
async def create_summary(request: SummaryRequest):
    """
    Génère des synthèses intelligentes et des commentaires pédagogiques au ton académique.
    Réduit la charge administrative tout en maintenant un feedback de haute qualité[cite: 61, 62].
    """
    try:
        return await llm_service.generate_academic_summary(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erreur lors de l'analyse académique : {str(e)}"
        )



@router.post(
    "/synthesize-speech", 
    response_model=AudioResponse,
    summary="Conversion texte-en-parole (TTS)",
    description="Permet l'accès aux informations pour les parents non alphabétisés[cite: 45, 47]."
)
async def text_to_speech(request: AudioRequest):
    """
    Transforme les résultats ou notifications en audio (MP3).
    Supporte les langues locales comme le Wolof pour renforcer l'inclusion parentale.
    """
    try:
        url = await audio_service.generate_speech(request)
        return AudioResponse(audio_url=url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Échec de la synthèse vocale : {str(e)}"
        )
        


@router.post(
    "/analyze-dropout", 
    response_model=RiskIndicator,
    summary="Détecter le risque de décrochage",
    description="Analyse les signaux faibles (notes, absences) pour identifier les élèves à risque[cite: 34, 36]."
)
async def detect_dropout(request: DropoutAnalysisRequest):
    """
    Produit un indicateur de risque explicable et ajustable pour les enseignants.
    """
    return ml_service.analyze_dropout_risk(request)



@router.post(
    "/predict-admission", 
    response_model=AdmissionResponse,
    summary="Prédire l'admissibilité et l'orientation",
    description="Analyse l'historique et les tendances pour orienter les décisions pédagogiques[cite: 39]."
)
async def predict_pathway(request: AdmissionRequest):
    """
    Retourne des indicateurs probabilistes pour l'aide à la planification scolaire[cite: 41, 42].
    """
    try:
        return ml_service.predict_admission_and_pathway(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
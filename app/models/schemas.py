from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# =============================================================================
# SECTION 1 : GÉNÉRATION AUTOMATIQUE DE CONTENUS (QUIZ, EXERCICES, DEVOIRS)
# Objectif : Optimiser la productivité pédagogique (Fonctionnalité 4) [cite: 52, 55]
# =============================================================================

class QuizQuestion(BaseModel):
    """
    Structure d'une question individuelle. 
    Garantit des sorties structurées et exploitables (Fonctionnalité 4)[cite: 56].
    """
    question: str = Field(
        ..., 
        description="L'énoncé précis de la question pédagogique "
    )
    options: List[str] = Field(
        ..., 
        min_items=4, 
        max_items=4, 
        description="Exactement 4 options de réponse pour garantir la flexibilité du format "
    )
    correct_answer: str = Field(
        ..., 
        description="La réponse exacte qui doit figurer parmi les options "
    )
    explanation: Optional[str] = Field(
        None, 
        description="Justification pédagogique pour renforcer la qualité de l'apprentissage [cite: 57, 61]"
    )

class QuizRequest(BaseModel):
    """
    Paramètres d'entrée pour la génération de contenu selon les critères enseignants[cite: 54].
    Intègre une approche RAG basée sur les cours en base de données.
    """
    subject: str = Field(..., example="Histoire", description="Matière concernée [cite: 54]")
    topic: str = Field(..., example="L'Empire du Mali", description="Sujet spécifique du cours [cite: 54]")
    level: str = Field(..., example="Lycée", description="Niveau académique cible [cite: 54]")
    difficulty: str = Field(
        default="intermédiaire", 
        description="Niveau de complexité : facile, intermédiaire, difficile [cite: 54]"
    )
    evaluation_type: str = Field(
        default="quiz", 
        description="Type de format : quiz, exercice ou devoir [cite: 54]"
    )
    count: int = Field(
        default=5, 
        ge=1, 
        le=20, 
        description="Nombre de questions (Limité à 20 pour maîtriser les coûts) [cite: 68]"
    )
    language: str = Field(default="Français", description="Langue de génération")
    context_document: Optional[str] = Field(
        None, 
        description="Contenu textuel extrait des PDF de la base de données (Approche RAG) [cite: 53]"
    )

class QuizResponse(BaseModel):
    """Réponse finale structurée pour intégration directe dans ReactJS[cite: 20, 56]."""
    questions: List[QuizQuestion]


# =============================================================================
# SECTION 2 : ANALYSE ACADÉMIQUE ET RÉSUMÉS (BULLETINS)
# Objectif : Aide à la décision et réduction de charge administrative (Fonctionnalité 5) [cite: 59, 61]
# =============================================================================

class AcademicData(BaseModel):
    """
    Données d'entrée pour l'analyse intelligente des performances[cite: 35, 60].
    """
    student_name: str = Field(..., description="Nom complet de l'étudiant")
    subjects_performance: Dict[str, float] = Field(
        ..., 
        example={"Maths": 15.5, "Wolof": 14.0}, 
        description="Moyennes par matière extraites de PostgreSQL [cite: 10, 41]"
    )
    attendance_rate: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Taux d'assiduité (Indicateur clé du décrochage) [cite: 35, 48]"
    )
    previous_comments: Optional[List[str]] = Field(
        None, 
        description="Historique des feedbacks pour analyse de tendance [cite: 40]"
    )

class SummaryRequest(BaseModel):
    """Requête pour générer une synthèse pédagogique[cite: 60]."""
    academic_data: AcademicData
    tone: str = Field(
        default="académique", 
        description="Ton du texte : académique, encourageant ou formel [cite: 62]"
    )
    language: str = Field(default="Français")

class SummaryResponse(BaseModel):
    """
    Synthèse analytique interprétable et validable par l'humain[cite: 37, 62].
    """
    analytical_summary: str = Field(..., description="Analyse globale de l'évolution académique [cite: 60]")
    teacher_comment: str = Field(..., description="Commentaire suggéré pour le bulletin scolaire [cite: 60, 62]")
    key_strengths: List[str] = Field(..., description="Points forts identifiés")
    areas_for_improvement: List[str] = Field(..., description="Axes de progression")


# =============================================================================
# SECTION 3 : ASSISTANCE VOCALE ET INCLUSION (TEXT-TO-SPEECH)
# Objectif : Accessibilité pour parents non alphabétisés (Fonctionnalité 3) [cite: 45, 46]
# =============================================================================

class AudioRequest(BaseModel):
    """
    Paramètres pour la synthèse vocale multilingue[cite: 48].
    Supporte le Wolof via le modèle Tiny Aya.
    """
    text: str = Field(..., min_length=1, description="Texte à convertir en voix [cite: 48]")
    language_code: str = Field(
        default="fr-FR", 
        example="wo-SN", 
        description="Code langue (fr-FR, en-US, ou wo-SN pour Wolof)"
    )
    voice_id: str = Field(
        default="Lea", 
        description="Identifiant de la voix (AWS Polly ou modèle local)"
    )

class AudioResponse(BaseModel):
    """Lien vers le contenu audio stocké sur AWS S3[cite: 11]."""
    audio_url: str = Field(..., description="URL publique ou présignée du fichier audio généré")
    format: str = Field(default="mp3")
    
    

class DropoutAnalysisRequest(BaseModel):
    """Données requises pour évaluer le risque de décrochage."""
    student_id: str
    current_grades: List[float] = Field(..., description="Liste des notes de la période actuelle")
    previous_grades: List[float] = Field(..., description="Liste des notes de la période précédente")
    absence_count: int = Field(..., ge=0, description="Nombre total d'absences")
    late_count: int = Field(0, ge=0, description="Nombre de retards")
    behavior_score: int = Field(10, ge=0, le=10, description="Note de comportement (sur 10)")

class RiskIndicator(BaseModel):
    """Indicateur synthétique de risque."""
    score: float = Field(..., description="Score de risque de 0 à 100")
    level: str = Field(..., description="Niveau de risque (Faible, Modéré, Élevé)")
    factors: List[str] = Field(..., description="Facteurs explicatifs détectés (signaux faibles)")
    recommendation: str = Field(..., description="Action pédagogique suggérée")
    
    
# --- SECTION : PRÉDICTION D'ADMISSIBILITÉ ET PARCOURS ---

class SubjectScore(BaseModel):
    subject: str
    score: float

class AdmissionRequest(BaseModel):
    """Données pour l'analyse d'admissibilité et d'orientation."""
    student_id: str
    target_pathway: str = Field(..., example="Série S1 (Sciences)")
    academic_history: List[SubjectScore] = Field(..., description="Historique des notes par matière")
    overall_average: float
    grade_trend: float = Field(..., description="Évolution des notes sur les 3 derniers trimestres")

class PathwayRecommendation(BaseModel):
    pathway_name: str
    probability: float = Field(..., ge=0, le=100, description="Probabilité de réussite en %")
    suitability_score: float = Field(..., description="Score d'adéquation basé sur les points forts")

class AdmissionResponse(BaseModel):
    """Résultat de l'analyse prédictive."""
    admission_probability: float = Field(..., description="Score probabiliste d'admissibilité")
    recommendations: List[PathwayRecommendation] = Field(..., description="Parcours recommandés")
    analysis_summary: str = Field(..., description="Justification explicite et réaliste de l'analyse")
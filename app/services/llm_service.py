import logging
from typing import Union
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings
from app.models.schemas import (
    QuizRequest, 
    QuizResponse, 
    SummaryRequest, 
    SummaryResponse
)

# Configuration du logging pour monitorer les performances en production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """
    Service d'intelligence générative pour Digital School utilisant l'infrastructure Groq.
    Fournit des capacités de création de contenu pédagogique et d'analyse académique.
    """

    def __init__(self):
        """
        Initialisation du moteur LLM via Groq.
        Modèle : Llama-3-8b (vitesse optimale) ou Llama-3-70b (précision maximale).
        L'utilisation de Groq garantit une latence quasi nulle pour les enseignants.
        """
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama3-8b-8192",  # Choix pragmatique pour le ratio vitesse/coût
            temperature=0.3,              # Basse pour garantir la rigueur factuelle
            max_tokens=4096
        )

    async def generate_quiz(self, data: QuizRequest) -> QuizResponse:
        """
        FONCTIONNALITÉ 4 : Génération automatique de quiz et devoirs.
        Implémente le RAG pour limiter l'IA aux contenus de la base de données.
        """
        logger.info(f"Génération de {data.evaluation_type} sur le sujet: {data.topic}")

        # 1. Définition du rôle expert (System Prompt)
        system_prompt = (
            "Tu es un expert en ingénierie pédagogique pour Digital School. "
            "Ta mission est de générer des questions d'évaluation rigoureuses. "
            "RÈGLE CRITIQUE : Tu dois utiliser UNIQUEMENT les informations du document fourni "
            "en contexte pour créer les questions. Ne fait pas appel à tes connaissances externes "
            "si elles contredisent ou dépassent le document source."
        )

        # 2. Construction du contexte RAG (Source de vérité)
        context_block = ""
        if data.context_document:
            context_block = f"\n--- DOCUMENT DE RÉFÉRENCE (SOURCE DE VÉRITÉ) ---\n{data.context_document}\n"

        # 3. Prompt Utilisateur détaillé
        user_prompt = (
            f"Type d'évaluation : {data.evaluation_type}\n"
            f"Matière : {data.subject} | Niveau : {data.level} | Difficulté : {data.difficulty}\n"
            f"Nombre de questions : {data.count} | Langue : {data.language}\n"
            f"{context_block}\n"
            "INSTRUCTIONS DE FORMATAGE :\n"
            "1. Produis exactement 4 options par question.\n"
            "2. Identifie clairement la réponse correcte.\n"
            "3. Rédige une explication pédagogique qui aide l'élève à comprendre son erreur.\n"
            "4. Utilise un ton académique formel."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])

        # 4. Exécution avec sortie structurée (Mapping automatique vers QuizResponse)
        chain = prompt | self.llm.with_structured_output(QuizResponse)
        
        try:
            return await chain.ainvoke({})
        except Exception as e:
            logger.error(f"Erreur lors de la génération du quiz : {str(e)}")
            raise e

    async def generate_academic_summary(self, data: SummaryRequest) -> SummaryResponse:
        """
        FONCTIONNALITÉ 5 : Résumés et commentaires académiques.
        Transforme les données froides (notes, absences) en feedbacks humains.
        """
        logger.info(f"Génération de résumé pour l'élève : {data.academic_data.student_name}")

        # 1. Définition du rôle (System Prompt)
        system_prompt = (
            "Tu es un conseiller pédagogique principal. Ton rôle est d'analyser les résultats "
            "trimestriels et de rédiger des commentaires professionnels pour les bulletins."
            "Tu dois être factuel, constructif et adopter un ton académique exemplaire."
        )

        # 2. Formatage des données de performance
        perf_data = "\n".join([f"- {m}: {n}/20" for m, n in data.academic_data.subjects_performance.items()])
        
        # 3. Prompt Utilisateur
        user_prompt = (
            f"Élève : {data.academic_data.student_name}\n"
            f"Performances par matière :\n{perf_data}\n"
            f"Taux d'assiduité : {data.academic_data.attendance_rate}%\n"
            f"Ton de rédaction souhaité : {data.tone}\n\n"
            "TÂCHES :\n"
            "1. Rédige une synthèse analytique globale de la période.\n"
            "2. Rédige le commentaire court qui sera imprimé sur le bulletin scolaire.\n"
            "3. Liste les 3 points forts majeurs.\n"
            "4. Liste les 3 axes d'amélioration prioritaires."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])

        # 4. Exécution avec mapping automatique vers SummaryResponse
        chain = prompt | self.llm.with_structured_output(SummaryResponse)
        
        try:
            return await chain.ainvoke({})
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse académique : {str(e)}")
            raise e

# Export d'une instance unique (Singleton) pour utilisation dans les endpoints
llm_service = LLMService()
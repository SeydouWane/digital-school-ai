import numpy as np
from typing import List
from app.models.schemas import DropoutAnalysisRequest, RiskIndicator, AdmissionRequest, AdmissionResponse, PathwayRecommendation

class MLService:
    """
    Service d'analyse prédictive pour l'aide à la décision pédagogique.
    """

    def analyze_dropout_risk(self, data: DropoutAnalysisRequest) -> RiskIndicator:
        factors = []
        risk_points = 0
        
        # 1. Analyse de l'évolution des notes (Signaux faibles) 
        avg_current = np.mean(data.current_grades) if data.current_grades else 0
        avg_previous = np.mean(data.previous_grades) if data.previous_grades else 0
        
        if avg_current < avg_previous:
            drop = avg_previous - avg_current
            risk_points += min(drop * 5, 30)  # Jusqu'à 30 points de risque
            if drop > 2:
                factors.append(f"Baisse significative des performances (-{drop:.1f} pts)")

        # 2. Analyse de l'absentéisme 
        if data.absence_count > 5:
            risk_points += 25
            factors.append(f"Augmentation anormale des absences ({data.absence_count})")
        
        # 3. Ruptures comportementales 
        if data.behavior_score < 5:
            risk_points += 20
            factors.append("Alerte sur le comportement académique")

        # Calcul du score final (Normalisé à 100)
        final_score = min(risk_points + (10 - data.behavior_score) * 2, 100)

        # Détermination du niveau 
        if final_score < 30:
            level = "Faible"
            recommendation = "Continuer le suivi standard."
        elif final_score < 70:
            level = "Modéré"
            recommendation = "Entretien pédagogique préventif recommandé."
        else:
            level = "Élevé"
            recommendation = "Alerte immédiate : Plan d'accompagnement nécessaire."

        return RiskIndicator(
            score=final_score,
            level=level,
            factors=factors if factors else ["Aucun signal critique détecté"],
            recommendation=recommendation
        )
    def predict_admission_and_pathway(self, data: AdmissionRequest) -> AdmissionResponse:
        """
        Estime les probabilités de réussite et suggère des parcours[cite: 38, 39].
        """
        # 1. Calcul de la probabilité d'admissibilité de base
        # On pondère la moyenne générale et la tendance d'évolution [cite: 41]
        base_prob = data.overall_average * 4  # Exemple simple : moyenne 15/20 -> 60%
        trend_bonus = data.grade_trend * 10    # Bonus/Malus selon l'évolution
        admission_prob = max(min(base_prob + trend_bonus, 98), 5) # Éviter 0% ou 100% 

        # 2. Analyse des parcours recommandés (Simulation de logique métier)
        # On identifie les points forts dans l'historique [cite: 40]
        science_scores = [s.score for s in data.academic_history if s.subject in ["Maths", "PC", "SVT"]]
        literary_scores = [s.score for s in data.academic_history if s.subject in ["Français", "Philosphie", "Histoire"]]
        
        avg_science = sum(science_scores) / len(science_scores) if science_scores else 0
        avg_literary = sum(literary_scores) / len(literary_scores) if literary_scores else 0

        recommendations = [
            PathwayRecommendation(
                pathway_name="Série Scientifique",
                probability=min(avg_science * 5 + trend_bonus, 95),
                suitability_score=avg_science
            ),
            PathwayRecommendation(
                pathway_name="Série Littéraire",
                probability=min(avg_literary * 5 + trend_bonus, 95),
                suitability_score=avg_literary
            )
        ]

        # 3. Synthèse interprétable [cite: 37, 44]
        top_path = max(recommendations, key=lambda x: x.probability)
        analysis = (
            f"L'élève présente une probabilité d'admissibilité de {admission_prob:.1f}% pour le parcours {data.target_pathway}. "
            f"L'analyse des résultats suggère une forte aptitude pour la {top_path.pathway_name} "
            f"avec un score d'adéquation de {top_path.suitability_score:.1f}/20."
        )

        return AdmissionResponse(
            admission_probability=admission_prob,
            recommendations=recommendations,
            analysis_summary=analysis
        )

ml_service = MLService()
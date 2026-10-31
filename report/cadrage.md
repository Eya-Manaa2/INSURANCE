# Note de Cadrage - Système Multi-Agents IA pour la Souscription en Assurance

**Date** : 30 Octobre 2026
**Phase** : Phase 0 - Cadrage

---

## 1. Contexte et Objectifs

### 1.1 Contexte
La souscription (underwriting) en assurance est un processus lent, coûteux et peu homogène. Les souscripteurs consultent manuellement des formulaires, des pièces justificatives, des grilles internes et des historiques de sinistres.

### 1.2 Objectif Principal
Concevoir et prototyper un système multi-agents IA pour la souscription en assurance automobile, capable de :
- Automatiser l'extraction et l'analyse des informations
- Produire une recommandation de décision avec score de risque
- Quantifier l'incertitude et déclencher l'escalade si nécessaire
- Mesurer et limiter les biais
- Fournir des explications compréhensibles
- Journaliser chaque étape pour l'audit

### 1.3 Contribution de Recherche
Étudier l'apport du multi-agents face à un agent unique sur 5 dimensions :
1. Collaboration multi-agents
2. Incertitude
3. Équité et biais
4. Explicabilité
5. Conformité réglementaire

---

## 2. Choix de la Branche d'Assurance

### 2.1 Choix : Assurance Automobile

**Justification** :
- Disponibilité de données publiques (Kaggle, UCI)
- Simplicité relative des variables (âge du véhicule, type, etc.)
- Documentation souscription publique accessible
- Pertinence pour démonstration

### 2.2 Exclusions
- Vie, santé, grands risques industriels (hors périmètre)
- Gestion des sinistres post-souscription (hors périmètre)

---

## 3. Données

### 3.1 Source de Données

**Données utilisées** :
- Source : Dataset public "Insurance Claims Dataset 2026" (Kaggle)
- Nombre de records : 5,000 (échantillon de 12,488 claims auto)
- Variables : âge, genre, région, crédit, véhicule, prime, claim, fraud risk score

**Limitation** :
- Données synthétiques/public research data
- Pas de données de production d'un vrai assureur
- Potentiellement US-centric (régions North/South/East/West)

### 3.2 Construction des Labels de Décision

**Règle appliquée** (conforme au cahier des charges) :
- Basée sur `fraud_risk_score` du dataset original
- `fraud_risk_score > 70` → Reject
- `fraud_risk_score > 50` → Accept with Surcharge
- `fraud_risk_score <= 50` → Accept Standard

**Justification** :
- Le dataset ne contient pas de labels de décision d'underwriting
- Cette règle est justifiable en pratique : un score de fraude élevé indique un risque inacceptable
- Permet de créer une classification supervisée pour entraîner le modèle ML

**Distribution obtenue** :
- Accept_Standard : 49.9%
- Accept_with_Surcharge : 20.5%
- Reject : 29.7%

### 3.3 Catalogue des Variables

| Variable | Type | Sensible | Description |
|-----------|------|----------|-------------|
| age | Numérique | ❌ | Âge du conducteur |
| gender | Catégorielle | ✅ | Genre du conducteur |
| region | Catégorielle | ❌ | Région géographique |
| credit_score | Numérique | ❌ | Score de crédit |
| vehicle_value | Numérique | ❌ | Valeur du véhicule |
| premium_amount | Numérique | ❌ | Montant de la prime |
| claim_amount | Numérique | ❌ | Montant du claim |
| fraud_flag | Binaire | ❌ | Indicateur de fraude (du dataset) |
| fraud_risk_score | Numérique | ❌ | Score de risque de fraude (du dataset) |

**Attributs sensibles** :
- `gender` est marqué comme sensible (protégé)
- `region` peut être un proxy de variables géographiques sensibles
- Ces variables ne seront PAS utilisées directement dans le modèle ML pour la décision

---

## 4. Questions de Recherche

### 4.1 Collaboration Multi-Agents
**H1** : Une architecture à débat ou à vote pondéré réduit les erreurs sur les dossiers ambigus par rapport à un agent unique.

**Méthode** : Comparer 4 schémas (pipeline, orchestrateur, débat, vote pondéré) contre baseline agent unique.

**Mesures** : Exactitude, F1, latence, taux de désaccord résolu.

### 4.2 Incertitude
**H2** : La prise en compte de l'incertitude (abstention + escalade) réduit fortement le taux d'erreur des décisions automatiques, au prix d'un taux d'automatisation plus faible.

**Méthode** : Calibration (MAPIE), ensembles, escalade si confiance < seuil.

**Mesures** : ECE, Brier score, courbe risque-couverture.

### 4.3 Équité et Biais
**H3** : Un agent équité dédié réduit les écarts de traitement sans dégrader fortement la performance.

**Méthode** : Tests de parité, tests contrefactuels, atténuation (post-processing).

**Mesures** : Parité démographique, égalité des chances, impact disproportionné.

### 4.4 Explicabilité
**H4** : Des explications ancrées dans des sources citées sont jugées plus utiles que des explications génériques.

**Méthode** : SHAP, DiCE (contrefactuels), citations RAG, évaluation humaine.

**Mesures** : Fidélité, stabilité, score de compréhension (panel 30-50 décisions).

### 4.5 Conformité Réglementaire
**H5** : Le système satisfait aux exigences de transparence, supervision humaine et protection des données.

**Méthode** : Journal d'audit, cartographie exigences → fonctions, tests de conformité.

**Mesures** : Couverture des exigences, complétude de la traçabilité.

---

## 5. Architecture Multi-Agents

### 5.1 Agents Spécialisés (6)

1. **Intake/Validation** : Réception, validation de complétude, normalisation
2. **Agent Client** : Analyse du profil, cohérence des déclarations, score de profil
3. **Agent Documents** : RAG sur conditions générales, vérification d'éligibilité
4. **Agent Risque** : Scoring ML (XGBoost) + règles actuarielles
5. **Agent Externe** : Données météo, zones à risque, registres publics
6. **Agent Sinistres** : Historique, fréquence/sévérité, signaux de fraude

### 5.2 Agents de Décision (2)

7. **Orchestrateur** : Planification, routage, détection de conflits
8. **Agent Décideur** : Agrégation, arbitrage, calcul d'incertitude

### 5.3 Agents de Gouvernance (3)

9. **Agent Équité** : Tests de biais, blocage si seuil dépassé
10. **Agent Conformité** : Vérification légale, RGPD, IA Act
11. **Agent Explication** : Explications globales et locales, contrefactuels

---

## 6. Baselines et Variantes

### 6.1 Baselines

- **B1** : Règles de souscription seules (if-then sur seuils)
- **B2** : Modèle ML seul (XGBoost sur variables tabulaires)
- **B3** : Agent LLM unique avec outils
- **B4** : Pipeline séquentiel d'agents

### 6.2 Variantes à Tester

- Avec/sans module d'incertitude
- Avec/sans agent équité
- Avec/sans agent d'explication
- 4 schémas de collaboration (pipeline, orchestrateur, débat, vote)

---

## 7. Protocole Expérimental

### 7.1 Split des Données
- Train : 70%
- Validation : 15%
- Test : 15%
- Split temporel si possible (pour éviter les fuites)

### 7.2 Mesures par Axe

| Axe | Mesures |
|-----|---------|
| Qualité de décision | Exactitude, F1, erreur sur prime |
| Robustesse | Résultats sous bruit, champs manquants |
| Incertitude | ECE, Brier, taux d'escalade pertinent |
| Équité | Parité, égalité des chances, écart contrefactuel |
| Explicabilité | Fidélité, évaluation humaine |
| Efficacité | Latence, coût en jetons, taux d'automatisation |
| Conformité | Couverture exigences, complétude journal |

### 7.3 Rigueur Statistique
- Plusieurs exécutions par configuration (LLM non déterministes)
- Moyenne et écart-type
- Tests de significativité
- Graine fixée quand possible
- Étude d'ablation

---

## 8. Stack Technique

- **Orchestration** : LangGraph
- **LLM** : OpenAI GPT-4 (prototypage) / Open source local (confidentialité)
- **RAG** : Chroma + sentence-transformers
- **Scoring** : scikit-learn, XGBoost
- **Incertitude** : MAPIE (prédiction conforme)
- **Équité** : Fairlearn
- **Explicabilité** : SHAP, DiCE
- **Interface** : Streamlit
- **Backend** : SQLite
- **MLOps** : MLflow

---

## 9. Planning (Accéléré)

**Phase actuelle** : Phase 0 - Cadrage ✅

**Prochaines phases** :
- Phase 1 : Données ✅ (terminé)
- Phase 2 : Baselines (en cours)
- Phase 3 : Agents spécialisés
- Phase 4 : Orchestration
- Phase 5 : Gouvernance
- Phase 6 : Expérimentation
- Phase 7 : Rédaction

---

## 10. Risques et Mitigation

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Données non représentatives | Élevée | Élevé | Reconnaître la limite dans le rapport |
| Hallucinations LLM | Moyenne | Élevé | RAG avec citations, vérifications croisées |
| Coût LLM élevé | Moyenne | Moyen | Budget de jetons, cache |
| Périmètre trop large | Élevée | Élevé | Focus sur auto, MVP simplifié |
| Biais difficiles à mesurer | Moyenne | Moyen | Tests contrefactuels, variables proxy |

---

## 11. Livrables

1. **Rapport** : État de l'art, conception, expériences, résultats
2. **Code** : Versionné, reproductible, scripts d'expériences
3. **Prototype** : Streamlit fonctionnel
4. **Données** : Dataset avec documentation
5. **Journal d'audit** : Exemple de traçabilité
6. **Rapport d'équité** : Mesures et analyse

---

**Statut** : Cadrage validé, prêt pour Phase 2 (Baselines)

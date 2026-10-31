# Multi-Agent AI for Insurance Underwriting - Research Project

🎓 **Projet de Fin d'Études - Système Multi-Agents IA pour la Souscription en Assurance**

---

## 🎯 Objectif

Concevoir et prototyper un système multi-agents IA pour la souscription en assurance, avec une contribution de recherche sur :
1. Collaboration multi-agents
2. Incertitude
3. Équité et biais
4. Explicabilité
5. Conformité réglementaire

---

## 📐 Périmètre

- **Branche** : Assurance Auto (à confirmer selon disponibilité des données)
- **Données** : Jeux publics/synthétiques (Kaggle, UCI)
- **Prototype** : Interface simple (Streamlit)
- **Focus** : Recherche expérimentale sur les agents

---

## 🔬 Axes de Recherche

### 1. Collaboration Multi-Agents
Comparer 4 schémas :
- Pipeline séquentiel
- Orchestrateur + spécialistes
- Débat/critique
- Vote pondéré par confiance
- Agent unique (baseline)

### 2. Incertitude
- Calibration (temperature scaling, prédiction conforme)
- Déclenchement d'escalade si confiance faible
- Mesures : ECE, Brier score

### 3. Équité et Biais
- Tests de parité démographique
- Tests contrefactuels
- Agent équité dédié
- Mesures : Parité, égalité des chances

### 4. Explicabilité
- SHAP pour importance des variables
- DiCE pour contrefactuels
- Citations du RAG
- Évaluation humaine

### 5. Conformité
- Journal d'audit inaltérable
- Vérification RGPD/IA Act
- Droit à explication

---

## 🤖 Architecture Multi-Agents

### Agents Spécialisés (6)
1. **Intake/Validation** - Réception, OCR, complétude
2. **Agent Client** - Analyse du profil, détection d'anomalies
3. **Agent Documents** - RAG sur conditions générales
4. **Agent Risque** - Scoring ML (XGBoost) + règles
5. **Agent Externe** - Données météo, zones à risque
6. **Agent Sinistres** - Historique, fraude

### Agents de Décision (2)
7. **Orchestrateur** - Planification, détection de conflits
8. **Agent Décideur** - Agrégation, arbitrage

### Agents de Gouvernance (3)
9. **Agent Équité** - Tests de biais
10. **Agent Conformité** - Vérification légale
11. **Agent Explication** - Explications adaptées

---

## 🧪 Expérimentation

### Baselines
- B1 : Règles de souscription seules
- B2 : Modèle ML seul (XGBoost)
- B3 : Agent LLM unique
- B4 : Pipeline séquentiel

### Variantes
- Avec/sans incertitude
- Avec/sans agent équité
- Avec/sans agent d'explication
- 4 schémas de collaboration

---

## 📦 Livrables

1. **Rapport** : État de l'art, conception, expériences, résultats
2. **Code** : Versionné, reproductible, scripts d'expériences
3. **Prototype** : Streamlit fonctionnel
4. **Données** : Jeux avec documentation
5. **Journal d'audit** : Exemple de traçabilité
6. **Rapport d'équité** : Mesures et analyse

---

## 🛠️ Stack Technique

- **Orchestration** : LangGraph
- **LLM** : OpenAI/Anthropic (prototypage)
- **RAG** : Chroma/FAISS
- **Scoring** : scikit-learn, XGBoost
- **Incertitude** : MAPIE
- **Équité** : Fairlearn/AIF360
- **Explicabilité** : SHAP, DiCE
- **Interface** : Streamlit
- **Backend** : SQLite

---

## 📁 Structure

```
multi-agent-underwriting-research/
├── data/                      # Données
│   ├── raw/                   # Données brutes
│   ├── processed/             # Données traitées
│   └── synthetic/             # Données synthétiques
├── experiments/              # Scripts d'expériences
│   ├── baselines/            # Baselines B1-B4
│   ├── collaboration/        # Schémas de collaboration
│   ├── uncertainty/          # Tests d'incertitude
│   ├── fairness/             # Tests d'équité
│   └── explainability/       # Tests d'explicabilité
├── agents/                   # Implémentation des agents
│   ├── intake.py
│   ├── client.py
│   ├── documents.py
│   ├── risk.py              # XGBoost model
│   ├── external.py
│   ├── claims.py
│   ├── orchestrator.py
│   ├── decider.py
│   ├── fairness.py
│   ├── compliance.py
│   └── explanation.py
├── models/                   # Modèles ML entraînés
├── knowledge_base/           # RAG corpus
│   ├── guidelines/
│   └── regulations/
├── streamlit/                # Interface prototype
│   └── app.py
├── utils/                    # Utilitaires
│   ├── data_processing.py
│   ├── audit.py
│   └── metrics.py
├── requirements.txt
├── README.md
└── report/                   # Rapport de recherche
    └── draft.md
```

---

## 🚀 Démarrage

```bash
# Installation
pip install -r requirements.txt

# Préparer les données
python utils/data_processing.py

# Entraîner le modèle ML
python experiments/baselines/train_model.py

# Exécuter une baseline
python experiments/baselines/baseline_ml.py

# Exécuter une expérience de collaboration
python experiments/collaboration/orchestrator.py

# Lancer le prototype
streamlit run streamlit/app.py
```

---

## 📈 Planning

- **Semaine 1-2** : Cadrage, collecte de données
- **Semaine 3-4** : Préparation des données, entraînement modèle ML
- **Semaine 5-6** : Baselines (B1-B4)
- **Semaine 7-9** : Agents spécialisés
- **Semaine 10-11** : Orchestration et schémas de collaboration
- **Semaine 12-13** : Gouvernance (incertitude, équité, conformité)
- **Semaine 14** : Expérimentation complète
- **Semaine 15-16** : Rédaction et démo

---

**Statut** : Phase 0 - Cadrage en cours

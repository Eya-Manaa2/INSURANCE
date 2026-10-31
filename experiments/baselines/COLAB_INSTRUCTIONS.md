# Instructions - Entraînement du Modèle ML sur Google Colab

## 📋 Étape 1 : Ouvrir Google Colab

1. Allez sur https://colab.research.google.com/
2. Cliquez sur "File" → "New notebook"
3. Ou chargez le notebook existant si vous l'avez téléchargé

## 📋 Étape 2 : Installer les dépendances

Copiez et exécutez cette cellule dans Colab :

```python
!pip install scikit-learn xgboost pandas numpy joblib
```

## 📋 Étape 3 : Charger le Dataset

1. Cliquez sur l'icône de dossier à gauche dans Colab
2. Cliquez sur l'icône "Upload" (flèche vers le haut)
3. Sélectionnez le fichier :
   - `labeled_research_data.json` (dans `experiments/baselines/`)

Ou téléchargez-le depuis votre projet local et uploadez-le.

## 📋 Étape 4 : Exécuter le Notebook

Exécutez toutes les cellules du notebook dans l'ordre :
1. Install Dependencies
2. Load Dataset
3. Prepare Features and Labels
4. Split Data
5. Train XGBoost Model
6. Feature Importance
7. Evaluate on Test Set
8. Save Model

## 📋 Étape 5 : Télécharger les fichiers entraînés

Une fois l'entraînement terminé, téléchargez ces fichiers depuis Colab :
- `underwriter_xgboost_model.pkl`
- `label_encoder.pkl`
- `feature_names.pkl`

## 📋 Étape 6 : Placer les fichiers dans le projet local

Placez ces fichiers dans votre projet local :
```
C:\DEVELOPER\multi-agent-underwriting-research\models\
├── underwriter_xgboost_model.pkl
├── label_encoder.pkl
└── feature_names.pkl
```

## 📋 Étape 7 : Me prévenir

Une fois les fichiers téléchargés et placés dans le projet, dites-moi et je continuerai avec l'intégration du modèle entraîné dans Baseline B2.

---

## 📊 Résultats attendus

Le modèle XGBoost devrait donner une accuracy supérieure à 57.64% (Baseline B1).
Typiquement : 70-85% accuracy sur ce type de dataset.

---

## 🚨 Si vous n'avez pas accès à Google Colab

Dites-moi et je continuerai avec :
- Option 2 : Implémenter les agents avec mock ML
- Option 4 : Simplifier et utiliser uniquement des règles

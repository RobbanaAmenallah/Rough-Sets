"""
Game Datasets and Content for RoughSet Challenge.
All decision tables are mathematically verified with roughset.py.
"""

# LEVEL 1: FEATURE HUNTER
# Mission: Discover dispensable attributes by removing features that do not affect classification.
LEVEL_1_DATA = {
    "level": 1,
    "title": "Feature Hunter",
    "subtitle": "Find the features that do NOT help classification.",
    "condition_attributes": ["Glasses", "Hair", "Hat", "Shirt", "Height"],
    "decision_attribute": "Decision",
    "objects": [
        # Obj 1 and Obj 2 differ ONLY in Glasses -> Glasses is Indispensable
        {"id": "Obj 1", "Glasses": "Yes", "Hair": "Dark",  "Hat": "No",  "Shirt": "Red",  "Height": "Tall",  "Decision": "Accept"},
        {"id": "Obj 2", "Glasses": "No",  "Hair": "Dark",  "Hat": "No",  "Shirt": "Red",  "Height": "Tall",  "Decision": "Reject"},
        # Obj 3 and Obj 4 differ ONLY in Shirt -> Shirt is Indispensable
        {"id": "Obj 3", "Glasses": "Yes", "Hair": "Blond", "Hat": "Yes", "Shirt": "Red",  "Height": "Short", "Decision": "Accept"},
        {"id": "Obj 4", "Glasses": "Yes", "Hair": "Blond", "Hat": "Yes", "Shirt": "Blue", "Height": "Short", "Decision": "Reject"},
        # Obj 5 and Obj 6 provide coverage where Hat and Height can be removed without conflict
        {"id": "Obj 5", "Glasses": "No",  "Hair": "Blond", "Hat": "Yes", "Shirt": "Red",  "Height": "Tall",  "Decision": "Reject"},
        {"id": "Obj 6", "Glasses": "No",  "Hair": "Blond", "Hat": "No",  "Shirt": "Red",  "Height": "Short", "Decision": "Reject"},
    ],
    "explanation": {
        "title": "WHAT YOU JUST DISCOVERED: DISPENSABLE ATTRIBUTE",
        "description": "You removed a feature without changing the required classification power (100%). In Rough Sets terminology, this feature is DISPENSABLE. Features whose removal destroys classification are INDISPENSABLE."
    }
}

# LEVEL 2: UNLOCK THE CORE
# Mission: Discover the indispensable attributes (the CORE) that cannot be removed.
LEVEL_2_DATA = {
    "level": 2,
    "title": "Unlock the CORE",
    "subtitle": "Some attributes cannot be removed without losing knowledge. Find the CORE.",
    "condition_attributes": ["Fever", "ThroatPain", "Cough", "Fatigue", "Headache"],
    "decision_attribute": "Diagnosis",
    "objects": [
        # Pair differing only in Fever with different diagnoses -> Fever is Indispensable
        {"id": "P1", "Fever": "High",   "ThroatPain": "Yes", "Cough": "Severe", "Fatigue": "High", "Headache": "Mild", "Diagnosis": "Flu"},
        {"id": "P2", "Fever": "Normal", "ThroatPain": "Yes", "Cough": "Severe", "Fatigue": "High", "Headache": "Mild", "Diagnosis": "Cold"},
        # Pair differing only in ThroatPain with different diagnoses -> ThroatPain is Indispensable
        {"id": "P3", "Fever": "High",   "ThroatPain": "No",  "Cough": "Severe", "Fatigue": "High", "Headache": "Mild", "Diagnosis": "Infection"},
        # Additional supporting cases with dispensable Fatigue/Headache
        {"id": "P4", "Fever": "Normal", "ThroatPain": "No",  "Cough": "Mild",   "Fatigue": "Low",  "Headache": "Severe", "Diagnosis": "Allergy"},
        {"id": "P5", "Fever": "Normal", "ThroatPain": "No",  "Cough": "Mild",   "Fatigue": "High", "Headache": "Mild",   "Diagnosis": "Allergy"},
        {"id": "P6", "Fever": "High",   "ThroatPain": "Yes", "Cough": "Mild",   "Fatigue": "Low",  "Headache": "Mild",   "Diagnosis": "Flu"}
    ],
    "explanation": {
        "title": "CORE UNLOCKED 🔐",
        "description": "The CORE contains the attributes that are indispensable with respect to the classification. Mathematically, it is the intersection of all valid REDUCTS."
    }
}

# LEVEL 3: REDUCT CHALLENGE
# Mission: Find a minimal subset of 8 attributes that preserves 100% classification power.
LEVEL_3_DATA = {
    "level": 3,
    "title": "Find the REDUCT",
    "subtitle": "Find a minimal feature subset that preserves full classification power.",
    "condition_attributes": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "decision_attribute": "Class",
    "objects": [
        {"id": "U1", "A": 1, "B": 0, "C": 1, "D": 1, "E": 0, "F": 1, "G": 0, "H": 1, "Class": "Alpha"},
        {"id": "U2", "A": 1, "B": 1, "C": 0, "D": 1, "E": 1, "F": 0, "G": 0, "H": 0, "Class": "Beta"},
        {"id": "U3", "A": 0, "B": 1, "C": 1, "D": 0, "E": 1, "F": 1, "G": 1, "H": 1, "Class": "Gamma"},
        {"id": "U4", "A": 0, "B": 0, "C": 0, "D": 1, "E": 0, "F": 0, "G": 1, "H": 0, "Class": "Delta"},
        {"id": "U5", "A": 1, "B": 0, "C": 1, "D": 0, "E": 1, "F": 0, "G": 0, "H": 1, "Class": "Beta"},
        {"id": "U6", "A": 0, "B": 1, "C": 0, "D": 1, "E": 0, "F": 1, "G": 1, "H": 0, "Class": "Alpha"},
        {"id": "U7", "A": 1, "B": 1, "C": 1, "D": 0, "E": 0, "F": 0, "G": 1, "H": 1, "Class": "Gamma"},
        {"id": "U8", "A": 0, "B": 0, "C": 1, "D": 1, "E": 1, "F": 0, "G": 0, "H": 0, "Class": "Delta"}
    ],
    "explanation": {
        "title": "REDUCT FOUND! 🎉",
        "description": "A REDUCT is a minimal subset of attributes that preserves the required classification/discernibility of the original feature set. No attribute can be removed without losing classification power."
    }
}

# LEVEL 4: FACE RECOGNITION LAB (PAPER CONNECTION)
# Pipeline: 10,304 pixels -> SVD (92) -> Heuristic (60) -> PCA (20) -> Rough Sets Reduct -> LVQ (97.3%)
LEVEL_4_DATA = {
    "level": 4,
    "title": "Face Recognition Lab",
    "subtitle": "From thousands of pixels to useful features using SVD, PCA, and Rough Sets.",
    "pipeline_steps": [
        {"step": 1, "name": "ORIGINAL FACE", "features": "112 × 92 pixels", "details": "10,304 raw pixel values"},
        {"step": 2, "name": "SVD (Singular Value Decomposition)", "features": "92 features", "details": "Linear algebraic decomposition"},
        {"step": 3, "name": "HEURISTIC REDUCTION", "features": "60 features", "details": "Eliminate low singular values"},
        {"step": 4, "name": "PCA (Principal Component Analysis)", "features": "20 features", "details": "Global statistical variance projection"},
        {"step": 5, "name": "DISCRETIZATION", "features": "Discretized intervals", "details": "Partition continuous values into Rough Set bins"},
        {"step": 6, "name": "ROUGH SETS REDUCT", "features": "Minimal Reduct", "details": "Selects decision-relative discriminative components"},
        {"step": 7, "name": "LVQ CLASSIFIER", "features": "Trained Classifier", "details": "Achieved 97.3% test accuracy on 38-case evaluation"}
    ],
    "condition_attributes": ["PC1", "PC2", "PC3", "PC4", "PC5", "PC6"],
    "decision_attribute": "Identity",
    "objects": [
        {"id": "Face 1", "PC1": "Low",  "PC2": "High", "PC3": "Low",  "PC4": "High", "PC5": "Mid",  "PC6": "Low",  "Identity": "Subject_A"},
        {"id": "Face 2", "PC1": "Low",  "PC2": "High", "PC3": "High", "PC4": "Low",  "PC5": "Low",  "PC6": "High", "Identity": "Subject_B"},
        {"id": "Face 3", "PC1": "High", "PC2": "Low",  "PC3": "Low",  "PC4": "High", "PC5": "High", "PC6": "High", "Identity": "Subject_C"},
        {"id": "Face 4", "PC1": "High", "PC2": "Low",  "PC3": "High", "PC4": "Low",  "PC5": "Mid",  "PC6": "Low",  "Identity": "Subject_D"},
        {"id": "Face 5", "PC1": "Low",  "PC2": "Low",  "PC3": "High", "PC4": "High", "PC5": "Low",  "PC6": "Mid",  "Identity": "Subject_A"},
        {"id": "Face 6", "PC1": "High", "PC2": "High", "PC3": "Low",  "PC4": "Low",  "PC5": "High", "PC6": "Mid",  "Identity": "Subject_B"}
    ]
}

# FINAL QUIZ (5 Questions)
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What is a REDUCT in Rough Set Theory?",
        "options": [
            {"key": "A", "text": "A set containing all possible attributes in the universe"},
            {"key": "B", "text": "The collection of deleted or noisy objects in the decision table"},
            {"key": "C", "text": "A minimal subset of attributes that preserves the required classification power"},
            {"key": "D", "text": "A deep neural network layer used for backpropagation"}
        ],
        "correct_key": "C",
        "explanation": "A REDUCT is a minimal subset of condition attributes that preserves the same dependency/classification power as the original full attribute set."
    },
    {
        "id": 2,
        "question": "What does the CORE of a decision table represent?",
        "options": [
            {"key": "A", "text": "A random sample of features used for training validation"},
            {"key": "B", "text": "The set of indispensable attributes common to all valid reducts"},
            {"key": "C", "text": "The list of conflicting objects in the boundary region"},
            {"key": "D", "text": "The principal eigenvalues produced by PCA"}
        ],
        "correct_key": "B",
        "explanation": "The CORE consists of attributes that cannot be eliminated without losing classification power. Mathematically, it is the intersection of all reducts."
    },
    {
        "id": 3,
        "question": "If removing an attribute from the condition set does NOT reduce the positive region or classification power, that attribute is:",
        "options": [
            {"key": "A", "text": "Indispensable"},
            {"key": "B", "text": "Dispensable"},
            {"key": "C", "text": "A decision class"},
            {"key": "D", "text": "An eigenvector"}
        ],
        "correct_key": "B",
        "explanation": "An attribute is dispensable when its removal preserves the target degree of dependency (classification power)."
    },
    {
        "id": 4,
        "question": "Why are PCA and Rough Sets combined in the face recognition paper?",
        "options": [
            {"key": "A", "text": "PCA performs continuous projection/reduction, then Rough Sets selects a minimal discrete subset for classification"},
            {"key": "B", "text": "PCA and Rough Sets are the exact same mathematical technique under different names"},
            {"key": "C", "text": "PCA is only used to compute color histograms while Rough Sets draws bounding boxes"},
            {"key": "D", "text": "Rough Sets replace the need for camera lenses while PCA adjusts lighting"}
        ],
        "correct_key": "A",
        "explanation": "PCA projects high-dimensional data along maximum variance directions, and Rough Sets performs discrete rule-based feature selection without losing classification ability."
    },
    {
        "id": 5,
        "question": "What is the primary objective of Feature Reduction in Machine Learning?",
        "options": [
            {"key": "A", "text": "To increase the file size of the dataset so models have more memory"},
            {"key": "B", "text": "To use fewer features while preserving the information necessary for the classification task"},
            {"key": "C", "text": "To convert all categorical values into random floating point numbers"},
            {"key": "D", "text": "To remove the target decision class completely from the dataset"}
        ],
        "correct_key": "B",
        "explanation": "Feature reduction reduces computational complexity, mitigates the curse of dimensionality, and eliminates redundancy while maintaining predictive accuracy ('Less Data. Same Knowledge.')."
    }
]

# ARTICLE COMPARISON MATRIX
ARTICLE_COMPARISONS = [
    {
        "game_title": "Remove Unnecessary Features",
        "game_desc": "You discarded attributes that did not reduce classification power.",
        "paper_title": "FEATURE SELECTION & REDUCTION",
        "paper_desc": "Filtering out redundant and noisy dimensions before training classifiers.",
        "icon": "trash-2"
    },
    {
        "game_title": "Features That Cannot Be Removed",
        "game_desc": "You identified attributes whose removal caused classification loss.",
        "paper_title": "THE CORE (INDISPENSABILITY)",
        "paper_desc": "The intersection of all reducts; essential attributes that must be retained.",
        "icon": "lock"
    },
    {
        "game_title": "Smallest Valid Feature Set",
        "game_desc": "You found minimal subsets that maintained 100% classification power.",
        "paper_title": "REDUCT GENERATION",
        "paper_desc": "Deriving minimal attribute subsets preserving discernibility and positive regions.",
        "icon": "scissors"
    },
    {
        "game_title": "Face Recognition Lab",
        "game_desc": "You reduced PCA components to feed a compact set into classification.",
        "paper_title": "SVD → PCA → ROUGH SETS → LVQ PIPELINE",
        "paper_desc": "The multi-stage hybrid pipeline achieving 97.3% accuracy on 38 face test cases.",
        "icon": "user-check"
    }
]

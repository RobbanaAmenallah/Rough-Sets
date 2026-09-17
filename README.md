# 🧠 RoughSet Challenge — Interactive Gamified Machine Learning Platform
### *A Didactic & Real-Time Competitive Web Platform for Rough Set Theory and Feature Reduction*

[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Firebase Firestore](https://img.shields.io/badge/Database-Firebase%20Firestore%20%2F%20SQLite3-orange?logo=firebase&logoColor=white)](https://firebase.google.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Server--Authoritative%20%26%20Real--Time%20Sync-cyan)](#-system-architecture--engineering)
[![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen?logo=pytest&logoColor=white)](#-mathematical-verification--test-suite)
[![Academic Project](https://img.shields.io/badge/Master%202-Paris%20Dauphine--PSL-purple)](https://dauphine.psl.eu/)

> **“Less Data. Same Knowledge.”**  
> *Can you reduce high-dimensional data without losing any classification power?*

---

## 📑 Table of Contents
1. [Executive Summary & Academic Vision](#-executive-summary--academic-vision)
2. [Research Paper Foundation & Theoretical Problem](#-research-paper-foundation--theoretical-problem)
3. [Formal Mathematical Engine (`roughset.py`)](#-formal-mathematical-engine-roughsetpy)
4. [Gamified Pedagogical Progression (Levels 1 to 4 + Quiz)](#-gamified-pedagogical-progression)
5. [Real-Time Classroom Management & Instructor Portal](#-real-time-classroom-management--instructor-portal)
6. [System Architecture & Engineering Highlights](#-system-architecture--engineering-highlights)
7. [Database Layer: Firebase Firestore & SQLite Dual Engine](#-database-layer-firebase-firestore--sqlite-dual-engine)
8. [UI/UX Design & Projector Experience](#-uiux-design--projector-experience)
9. [Mathematical Verification & Test Suite](#-mathematical-verification--test-suite)
10. [Installation, Local Run & Cloud Deployment](#-installation-local-run--cloud-deployment)
11. [Project Structure](#-project-structure)
12. [Author & Academic Credits](#-author--academic-credits)

---

## 🎯 Executive Summary & Academic Vision

The **RoughSet Challenge** is a full-stack, real-time educational web application engineered for university amphitheaters and Machine Learning Master's courses at **Paris Dauphine University - PSL** (*Fundamentals of Machine Learning*).

Traditional teaching of algebraic machine learning models often suffers from abstract mathematical formalisms. This project bridges pure mathematics and interactive software engineering by transforming **Pawlak’s Rough Set Theory (1982)** and the research paper *"Rough Sets Methods in Feature Reduction and Classification"* into a **6-to-8 minute competitive, server-authoritative live classroom game**.

### Key Highlights
- **100% Pure Python Mathematical Engine**: Exact symbolic computations of Indiscernibility Classes ($\text{IND}$), Approximations ($B_*, B^*$), Positive Region ($\text{POS}$), Dependency Degree ($\gamma$), Attribute Dispensability, exhaustive minimal $\text{REDUCT}$s, and the $\text{CORE}$.
- **Server-Authoritative Anti-Cheat Gameplay**: Every feature toggle, core submission, and reduct selection is verified on the backend via mathematical proofs before awarding XP.
- **Real-Time Live Synchronization**: 2.5-second live polling between mobile students, teacher control room, and high-resolution projector podiums without requiring manual page reloads.
- **Dual-Layer Database Architecture**: Production-grade Google Cloud Firebase Firestore integration with a fault-tolerant, auto-fallback local SQLite engine.
- **Direct Research Paper Application**: Simulates the exact multi-stage dimensionality reduction pipeline (10,304 raw face image pixels $\to$ SVD/PCA $\to$ Rough Sets $\to$ 97.3% accuracy LVQ classifier).

---

## 🔬 Research Paper Foundation & Theoretical Problem

High-dimensional data domains (such as face biometrics, genomics, or signal processing) present severe challenges:
1. **The Curse of Dimensionality**: Exponential increase in computational volume and risk of overfitting.
2. **Redundant & Noisy Features**: Many features add zero classification value while increasing model complexity.
3. **Loss of Interpretability in Black-Box Models**: Statistical dimensionality reduction techniques (e.g., PCA, SVD) create transformed, non-interpretable linear combinations of variables.

### The Rough Sets Solution
**Rough Set Theory**, introduced by Professor **Zdzisław Pawlak**, provides an objective, data-driven approach to feature selection that:
- Does not require prior probability distributions or membership functions (unlike Bayesian statistics or Fuzzy Sets).
- Operates directly on granular equivalence classes of objects.
- Finds **minimal subsets of original, untransformed features** ($\text{REDUCT}$s) that preserve 100% of the original decision-making power ($\gamma$).

---

## 📐 Formal Mathematical Engine (`roughset.py`)

All computations in the platform are powered by the custom module [`roughset.py`](file:///c:/Users/robba/OneDrive/Bureau/Dauphine_M2/Fundamentals of ML/roughsetsproject/roughset.py).

### 1. Information System & Decision Table
An information system is a 4-tuple:
$$\mathcal{S} = (U, A, V, f)$$
where:
- $U = \{x_1, x_2, \dots, x_n\}$ is the non-empty, finite universe of objects.
- $A = C \cup \{d\}$ is the set of attributes, partitioned into condition attributes $C$ and decision attribute $d$ ($C \cap \{d\} = \emptyset$).
- $V = \bigcup_{a \in A} V_a$ is the domain of attribute values.
- $f : U \times A \to V$ is the information function such that $f(x, a) \in V_a$.

---

### 2. Indiscernibility Relation ($\text{IND}$)
For any attribute subset $B \subseteq A$, the indiscernibility relation $\text{IND}(B)$ is an equivalence relation on $U$:
$$\text{IND}(B) = \{ (x, y) \in U \times U \mid \forall a \in B, \; f(x, a) = f(y, a) \}$$

The equivalence classes of $\text{IND}(B)$ form a partition of the universe, denoted $U/\text{IND}(B)$ or $U/B$.

---

### 3. Lower and Upper Approximations
Let $X \subseteq U$ be a target set of objects belonging to a decision class. $X$ can be approximated using only information in $B$:
- **$B$-Lower Approximation** (Objects that *certainly* belong to $X$):
  $$\underline{B}(X) = B_*(X) = \bigcup \{ E \in U/B \mid E \subseteq X \}$$
- **$B$-Upper Approximation** (Objects that *possibly* belong to $X$):
  $$\overline{B}(X) = B^*(X) = \bigcup \{ E \in U/B \mid E \cap X \neq \emptyset \}$$
- **$B$-Boundary Region** (Objects of doubtful classification):
  $$\text{BN}_B(X) = \overline{B}(X) \setminus \underline{B}(X)$$

A set $X$ is **exact** if $\text{BN}_B(X) = \emptyset$; otherwise, $X$ is **rough**.

---

### 4. Positive Region and Degree of Dependency ($\gamma$)
Given decision classes $U/d = \{X_1, X_2, \dots, X_k\}$, the **$B$-Positive Region** is the set of all objects in $U$ that can be classified with certainty into classes of $U/d$ using attributes $B$:
$$\text{POS}_B(d) = \bigcup_{i=1}^k \underline{B}(X_i)$$

The **Degree of Dependency** ($\gamma_B(d) \in [0, 1]$), also referred to as the **Classification Power**, measures the proportion of correctly classifiable objects:
$$\gamma_B(d) = \frac{|\text{POS}_B(d)|}{|U|}$$

---

### 5. Dispensability, REDUCT, and CORE

#### A. Dispensable vs. Indispensable Attributes
An attribute $a \in B$ is **dispensable** with respect to decision $d$ if its removal does not reduce classification power:
$$\gamma_{B \setminus \{a\}}(d) = \gamma_B(d)$$
Otherwise, $a$ is **indispensable**.

#### B. REDUCT
A subset $R \subseteq C$ is a **REDUCT** of $C$ with respect to $d$ if and only if:
1. **Preservation of Quality**: $\gamma_R(d) = \gamma_C(d)$
2. **Minimality (Irreducibility)**: $\forall a \in R, \; \gamma_{R \setminus \{a\}}(d) < \gamma_C(d)$

$$\text{REDUCT}(C, d) = \{ R \subseteq C \mid \gamma_R(d) = \gamma_C(d) \land \forall r \in R, \gamma_{R \setminus \{r\}}(d) < \gamma_C(d) \}$$

#### C. CORE
The **CORE** is the intersection of all possible REDUCTs. It represents the set of condition attributes that cannot be eliminated from any reduct without causing information loss:
$$\text{CORE}(C, d) = \bigcap_{R \in \text{REDUCT}(C, d)} R = \{ a \in C \mid \gamma_{C \setminus \{a\}}(d) < \gamma_C(d) \}$$

---

## 🎮 Gamified Pedagogical Progression

The game is structured into 4 sequential didactic levels, a scientific quiz, and an interactive paper comparison matrix:

```
[ Mission Briefing ]
         │
         ▼
┌──────────────────┐
│ Level 1: Hunter  │ ➔ Identifies Dispensable Attributes (+100 XP / -25 XP penalty)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Level 2: CORE    │ ➔ Computes Irreplaceable Attributes (The CORE) (+150 XP per core attr)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Level 3: REDUCT  │ ➔ Assembles a Minimal Independent REDUCT (+500 XP + First-Try Bonus)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Level 4: FaceLab │ ➔ Simulates 10,304 Pixels ➔ SVD ➔ PCA ➔ Rough Sets (+400 XP)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Stage 5: Quiz    │ ➔ 5 Server-Validated Theoretical Questions (+500 XP)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Live Leaderboard │ ➔ Real-Time Projector Podium & Dynamic Analytics
└──────────────────┘
```

### Level-by-Level Breakdown

| Level | Mission Name | Educational Concept | Game Mechanic |
|---|---|---|---|
| **Level 1** | **Feature Hunter** | Dispensability & Noise Removal | Students click attributes to temporarily remove them. Live meter shows $\gamma$ change. Remove dispensable: **+100 XP**; Remove indispensable: **-25 XP penalty**. |
| **Level 2** | **Unlock the CORE** | Mathematical $\text{CORE} = \bigcap \text{Reducts}$ | Students analyze the table and find attributes whose deletion immediately damages $\gamma$. Success reveals the CORE box. |
| **Level 3** | **REDUCT Master** | Minimal Feature Subsets | Multi-select toggle pills. Students must achieve 100% $\gamma$ with the absolute minimal number of features. First-try bonus: **+200 XP**. |
| **Level 4** | **Face Recognition Lab** | Research Paper Case Study | Real-world simulation: 10,304 raw pixels $\to$ SVD (eigenfeatures) $\to$ PCA $\to$ Rough Set REDUCT (3 features) $\to$ 97.3% accuracy LVQ classifier. |
| **Quiz** | **Mastery Evaluation** | Theory Synthesis | 5 server-authoritative randomized questions checking depth of understanding (Dispensability, Approximations, Core, Noise tolerance). |

---

## 👨‍🏫 Real-Time Classroom Management & Instructor Portal

The dedicated instructor portal (`/admin`) allows professors to conduct live competitive sessions with zero manual friction:

```
                  ┌───────────────────────────────┐
                  │    INSTRUCTOR PORTAL (/admin) │
                  │  Session Code: RS8371 [LIVE]  │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│     STUDENT CLIENTS (/join)     │      │   PROJECTOR SCREEN (/leaderboard)│
│  - Instant Join via Code        │      │  - Dynamic 1st/2nd/3rd Podium   │
│  - Server-Authoritative Timer   │      │  - Live Scoreboard Animation    │
│  - Anti-Cheat XP Validation     │      │  - Automatic Confetti on Finish │
└─────────────────────────────────┘      └─────────────────────────────────┘
```

### Instructor Controls:
- **1-Click Session Generation**: Generates 6-character room codes (e.g., `RS8371`).
- **Dynamic Admission Gate**: `OPEN / CLOSE JOINING` allows teachers to lock the room when the challenge starts.
- **Live Sync Polling (2.5 seconds)**: Automatically refreshes real-time metrics (*Players Joined*, *Completed*, *Average Score*, *Average Duration*) and the live student roster without reloading the page.
- **Podium Trigger (`END CHALLENGE`)**: Forces the projector leaderboard to reveal the final winners and fire celebration confetti.
- **CSV Data Export (`/admin/export`)**: 1-click download of all student metrics, ranks, levels, timestamps, and XP for course grading.

---

## 🏗️ System Architecture & Engineering Highlights

```
┌────────────────────────────────────────────────────────────────────────┐
│                                CLIENT                                  │
│   Mobile / Laptop (Student)     │      Amphitheater Projector Screen   │
│   HTML5 / Modern CSS / Vanilla JS│      Dynamic Podium & Live Table     │
└───────────────────┬────────────────────────────┬───────────────────────┘
                    │ REST APIs (JSON)           │ 2.5s Polling Sync
                    ▼                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           FLASK BACKEND                                │
│   app.py (Route Controller, Anti-Cheat Verification, Session Engine)   │
└─────────┬──────────────────────────────┬───────────────────────────────┘
          │                              │
          ▼                              ▼
┌───────────────────────────┐  ┌─────────────────────────────────────────┐
│    ROUGH SET ENGINE       │  │          DUAL DATABASE LAYER            │
│       roughset.py         │  │              database.py                │
│  - IND Class Partitioning │  ├────────────────────┬────────────────────┤
│  - POS & Gamma Calculation│  │  PRIMARY (Cloud)   │  FALLBACK (Local)  │
│  - Exhaustive REDUCTs     │  │ Google Cloud       │ SQLite3            │
│  - CORE Intersection      │  │ Firebase Firestore │ Embedded DB        │
└───────────────────────────┘  └────────────────────┴────────────────────┘
```

### Security & Anti-Cheat Features
- **Server-Side Validation**: Clients never dictate scores or level completions. All XP arithmetic is computed on the backend based on mathematical verification of the student's submitted features.
- **Session Protection**: Secured Flask session cookies with cryptographic signing (`SECRET_KEY`).
- **Answer Farming Prevention**: Quiz responses and level completions enforce atomic uniqueness constraints.

---

## 🗄️ Database Layer: Firebase Firestore & SQLite Dual Engine

The data access layer [`database.py`](file:///c:/Users/robba/OneDrive/Bureau/Dauphine_M2/Fundamentals of ML/roughsetsproject/database.py) features a robust **dual-layer architecture**:

1. **Production Layer — Google Cloud Firebase Firestore**:
   - Cloud NoSQL document storage for multi-instance deployments (e.g. Render, Heroku, AWS).
   - Collections: `classroom_sessions`, `players`, `game_progress`, `level_completions`, `quiz_answers`.
   - Optimized indexing on `classroom_session_id` and `created_at`.
2. **Local / Fallback Layer — Embedded SQLite3**:
   - If Firebase credentials are not provided or API calls return an error, the platform automatically and silently falls back to local SQLite (`roughset_local.db`).
   - Ensures zero-configuration local development and 100% offline uptime during lectures.

---

## 🎨 UI/UX Design & Projector Experience

- **Cyberpunk AI Laboratory Theme**: Deep Navy (`#0B0F19`), Neon Cyan (`#06B6D4`), Electric Violet (`#8B5CF6`), and Emerald Green (`#10B981`).
- **Glassmorphism & Micro-Interactions**: Translucent frosted cards, glowing borders, and reactive hover animations.
- **Mobile Responsive Layout**: Scaled touch targets for students playing on smartphones.
- **High-Contrast Projector View**: Specially optimized typography and podium scaling for large lecture hall screens.

---

## 🧪 Mathematical Verification & Test Suite

The project includes an automated test suite verifying both mathematical integrity and web routing:

```bash
python -m unittest discover tests
```

### Test Coverage Summary:
- [`tests/test_roughset.py`](file:///c:/Users/robba/OneDrive/Bureau/Dauphine_M2/Fundamentals of ML/roughsetsproject/tests/test_roughset.py):
  - Correctness of $\text{IND}$ equivalence classes.
  - Correctness of $\text{POS}$ and $\gamma$ values ($\gamma \in [0, 1]$).
  - Algebraic identity: $\text{CORE}(C, d) = \bigcap_{R \in \text{REDUCTs}} R$.
  - Exact classification invariance under valid REDUCTs.
- [`tests/test_game_data.py`](file:///c:/Users/robba/OneDrive/Bureau/Dauphine_M2/Fundamentals of ML/roughsetsproject/tests/test_game_data.py):
  - Mathematical verification of all game datasets (Levels 1, 2, 3, 4).
  - Verification that every level contains at least one mathematically proven minimal REDUCT.
- [`tests/test_routes.py`](file:///c:/Users/robba/OneDrive/Bureau/Dauphine_M2/Fundamentals of ML/roughsetsproject/tests/test_routes.py):
  - End-to-end testing of student joining, mission start, level submission, quiz answering, and admin live polling.

---

## 🚀 Installation, Local Run & Cloud Deployment

### 1. Local Setup
```bash
# Clone the repository
git clone https://github.com/RobbanaAmenallah/Rough-Sets.git
cd Rough-Sets

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory:
```env
PORT=5005
FLASK_SECRET_KEY=roughsets_super_secret_production_key_2024
ADMIN_USERNAME=Amenallah
ADMIN_PASSWORD=Amen1920

# Optional: Path to Firebase service account JSON
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
```

### 3. Launch the Server
```bash
python app.py
```
Open **`http://localhost:5005`** in your browser.

---

## 📁 Project Structure

```
roughsetsproject/
├── app.py                     # Main Flask Application (Routes, APIs, Security)
├── roughset.py                # Pure Python Rough Set Mathematical Engine
├── game_data.py               # Mathematically Verified Datasets & Quiz Data
├── database.py                # Dual Database Layer (Firebase Firestore & SQLite)
├── requirements.txt           # Project Dependencies
├── Procfile                   # Cloud Deployment (Render / Gunicorn)
├── render.yaml                # Render Infrastructure-as-Code Spec
├── serviceAccountKey.json     # Firebase Credentials
│
├── static/
│   ├── css/
│   │   └── style.css          # AI Lab Glassmorphism Theme & Responsive Layout
│   └── js/
│       ├── main.js            # Client Game Controller (Levels 1-4, XP Hud)
│       ├── admin.js           # Real-Time 2.5s Instructor Polling Sync
│       ├── leaderboard.js     # Live Projector Sync & Podium Controller
│       └── confetti.js        # Canvas Particle Celebration System
│
├── templates/
│   ├── base.html              # Base Jinja2 Template & Navigation
│   ├── index.html             # Homepage & Role Selector
│   ├── join.html              # Student Session Entry
│   ├── mission.html           # Mission Briefing & Timer Initialization
│   ├── level1.html            # Level 1: Feature Hunter
│   ├── level2.html            # Level 2: Unlock the CORE
│   ├── level3.html            # Level 3: REDUCT Master
│   ├── level4.html            # Level 4: Face Lab Simulation
│   ├── quiz.html              # Post-Game Comprehension Quiz
│   ├── result.html            # Individual Student Score & Review
│   ├── leaderboard.html       # Projector Live Podium & Ranks
│   ├── admin_login.html       # Instructor Authentication
│   ├── admin.html             # Instructor Live Command Center
│   ├── article_connection.html# Theoretical Research Paper Bridge
│   └── demo.html              # Standalone Presenter Sandbox
│
└── tests/
    ├── test_roughset.py       # Mathematical Verification of Rough Sets
    ├── test_game_data.py      # Dataset Consistency & Solvability Tests
    └── test_routes.py         # Flask API & Session End-to-End Tests
```

---

## 👨‍💻 Author & Academic Credits

- **Author**: **Amenallah Robbana**
- **Institution**: **Université Paris Dauphine - PSL**
- **Degree**: **Master 2 — Fundamentals of Machine Learning**
- **Theoretical Reference**: 
  - Pawlak, Z. (1982). *Rough sets*. International Journal of Computer & Information Sciences, 11(5), 341-356.
  - *Rough Sets Methods in Feature Reduction and Classification*.

---

<div align="center">
  <sub>Designed & Developed with ❤️ for Machine Learning Education • Paris Dauphine-PSL</sub>
</div>

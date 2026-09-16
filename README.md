# 🧠 RoughSet Challenge

> **“Can you reduce the data without losing the knowledge?”**
> 
> An interactive educational AI puzzle game built for university lectures and presentations to help students master Rough Set Theory, Feature Reduction, CORE, REDUCT, and their real-world application to Face Recognition (based on *"Rough Sets Methods in Feature Reduction and Classification"*).

---

## 🎯 Game & Learning Objectives

Instead of reading abstract definitions, students interactively discover concepts:
1. **Dispensable vs. Indispensable Attributes** (Level 1: Feature Hunter)
2. **The CORE** as the set of irreplaceable attributes (Level 2: Unlock the CORE)
3. **REDUCT Generation** as finding minimal feature subsets preserving 100% discernibility (Level 3: REDUCT Master)
4. **Face Recognition Dimensionality Reduction Pipeline** from 10,304 raw pixels $\to$ SVD $\to$ PCA $\to$ Rough Sets REDUCT $\to$ LVQ Classifier with 97.3% reported accuracy (Level 4: Face Lab)
5. **Post-Game Comprehension Quiz** (5 server-validated questions)
6. **Academic Bridge** directly linking game mechanics to the research paper.

---

## 🛠️ Technology Stack

- **Backend:** Python 3, Flask, Jinja2, Flask sessions.
- **Mathematical Engine:** `roughset.py` — Real calculations of Indiscernibility ($IND$), Positive Region ($POS$), Degree of Dependency ($\gamma$), Dispensability, minimal REDUCTS, and CORE.
- **Database:** Supabase PostgreSQL (`supabase/schema.sql`) with seamless local SQLite fallback for instant zero-configuration testing.
- **Frontend:** HTML5, Modern CSS3 (Dark AI Lab aesthetic with cyan/purple glassmorphism), Vanilla JavaScript, Lucide Icons.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Clone / Open Directory & Install Dependencies
```bash
cd roughsetsproject
pip install -r requirements.txt
```

### 3. (Optional) Configure Firebase Cloud Firestore Database
To connect your persistent Firebase Firestore database for production / hosting:
1. Go to [console.firebase.google.com](https://console.firebase.google.com) and create a project (Free tier / Spark plan has generous free quotas).
2. Create a **Firestore Database** in test mode (or production rules).
3. Go to **Project Settings ⚙️ $\to$ Service Accounts**.
4. Click **Generate New Private Key** to download the JSON file.
5. Place the file in the project directory as `firebase-key.json` (or paste its content into `.env` as `FIREBASE_CREDENTIALS_JSON`).
6. Configure `.env`:
```env
FIREBASE_CREDENTIALS_PATH=firebase-key.json
FLASK_SECRET_KEY=roughset_secret_super_key_2024_secure
PORT=5005
ADMIN_USERNAME=Amenallah
ADMIN_PASSWORD=Amen1920
```
*(Note: If no Firebase key is present, the app automatically runs in local SQLite mode with zero configuration!)*

### 4. Run the Application
```bash
python app.py
```
Or with Flask CLI:
```bash
flask --app app run --debug
```

Visit: **`http://localhost:5005`** in your browser.

---

## 🧪 Running Automated Tests

Run the mathematical verification suite:
```bash
python -m unittest discover tests
```
This tests:
- Indiscernibility class partitioning
- Positive region and dependency degree ($\gamma$)
- Exhaustive minimal REDUCT discovery
- $CORE = \bigcap \text{Reducts}$ identity
- Mathematical consistency of Level 1, 2, 3, and 4 datasets.

---

## 👨‍🏫 Classroom Teaching Workflow

1. **Instructor:**
   - Go to `http://localhost:5005/admin/login` (Default: `Amenallah` / `Amen1920`).
   - Click **[ CREATE NEW CHALLENGE ]** to generate a classroom code (e.g. `RS4821`).
   - Open **[ PROJECTOR LEADERBOARD ]** on the classroom projector screen.
2. **Students:**
   - On their phones/laptops, go to `http://localhost:5005/join`.
   - Enter the session code `RS4821` and their first name.
   - Click **[ ACCEPT MISSION ]** to start their individual timer.
   - Play through Levels 1 to 4, complete the Quiz, and see their rank.
3. **Finish:**
   - The instructor clicks **[ END CHALLENGE ]** in the Admin dashboard.
   - The projector leaderboard triggers podium animations and congratulates the winners.
   - The instructor can export the full class performance via **[ EXPORT CSV ]**.

---

## 📐 Mathematical Formulation Reference

$$\text{IND}(B) = \{ (x, y) \in U \times U \mid \forall a \in B, a(x) = a(y) \}$$

$$\text{POS}_B(D) = \bigcup_{X \in U/D} B_*(X)$$

$$\gamma_B(D) = \frac{|\text{POS}_B(D)|}{|U|}$$

$$\text{Attribute } a \in B \text{ is dispensable} \iff \gamma_{B \setminus \{a\}}(D) = \gamma_B(D)$$

$$\text{REDUCT}(C, D) = \{ R \subseteq C \mid \gamma_R(D) = \gamma_C(D) \text{ and } \forall r \in R, \gamma_{R \setminus \{r\}}(D) < \gamma_C(D) \}$$

$$\text{CORE}(C, D) = \bigcap_{R \in \text{Reducts}(C, D)} R$$

---

## 📄 License
Educational use for Dauphine University / Machine Learning presentations.
Less Data. Same Knowledge.

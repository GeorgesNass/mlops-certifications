# FastAPI Exam Project – Quiz Generator

## Overview
FastAPI REST API for generating quizzes (QCM) from a CSV dataset.
Designed for an **educational / exam context**, demonstrating:
- FastAPI endpoints
- HTTP Basic authentication
- Custom error handling
- CSV persistence
- EDA and API testing with curl

---

## Project Structure

```
fastapi/
├── main.py
├── setup.sh
├── requirements.txt
├── README.md
├── src/
│   ├── core/        # auth, data access, exceptions
│   ├── models/      # Pydantic schemas
│   └── tools/       # EDA and testing scripts
├── data/            # questions.csv
├── requests/        # curl examples
├── eda_plots/       # EDA outputs
└── results/         # execution outputs
```


---


## Errors and Exceptions

- `401` → Authentification invalide
- `403` → Accès refusé (admin)
- `404` → Questions introuvables
- `422` → Données invalides (FastAPI)

---

## Prerequisites
- Python >= 3.8
- pip / venv
- curl
- spaCy model: fr_core_news_sm

---

## Windows & WSL2 Prerequisites

### PowerShell
```powershell
wsl --status
wsl --install
wsl --list --online
wsl --install -d Ubuntu
wsl -d Ubuntu
docker --version
docker compose version
```

### Ubuntu
```bash
sudo apt update
sudo apt install -y git
git --version
```

### Python
```bash
python3 --version
sudo apt install -y python3-pip python3-venv
```

---

## Setup

### Manual installation
```bash
cd ~/Desktop/git_projects/
python -m venv .fastapi_env
source .fastapi_env/bin/activate ## .fastapi_env\Scripts\activate.bat for windows
pip install --upgrade pip
pip install -r requirements.txt
python -m pip install --upgrade pip setuptools wheel
python -m pip install https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.5.0/fr_core_news_sm-3.5.0-py3-none-any.whl

```

### Interactive script
```bash
cd fastapi
chmod +x setup.sh
./setup.sh
```

---

## API Overview
- GET /verify – healthcheck  
- POST /generate_quiz – quiz generation (auth required)  
- POST /create_question – admin-only CSV insertion  

Custom handlers: 400, 401, 404, 422.

---

## EDA
```bash
python3 src/tools/eda_questions.py
```
Outputs are saved in `eda_plots/`.

---

## API Testing
```bash
python3 src/tools/test.py
python3 src/tools/multithreading.py sync 5
```


---

## Author
Georges Nassopoulos  
Email: georges.nassopoulos@gmail.com  
Status: Educational / Exam project
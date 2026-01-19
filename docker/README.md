# Docker – MLOps Certification

Docker-based orchestration and automated testing of a secured FastAPI service as part of an MLOps certification exam.

---

## 📌 Context

This project is part of a broader **MLOps / ML engineering training and certification path**.
It focuses on containerization, service orchestration, and automated testing using Docker and Docker Compose.

The objective is to validate **authentication**, **authorization**, and **content access** through isolated test containers, following exam requirements.

---

## 🗂️ Project Structure

```text
.
├─ docker-compose.yml        # Orchestrates all test containers
├─ setup.sh                  # Execution helper script
├─ log.txt                   # Execution trace (exam context)
│
├─ auth_test/                # Authentication tests
│  ├─ Dockerfile
│  └─ test_auth.py
│
├─ authorization_test/       # Authorization tests
│  ├─ Dockerfile
│  └─ test_authorization.py
│
├─ content_test/             # Content access tests
│  ├─ Dockerfile
│  └─ test_content.py
│
├─ logs/
│  └─ api_test.log           # Runtime logs
│
└─ deliverable/
   └─ exam_NASSOPOULOS.tar   # Original exam deliverable (required format)
```

---

## 🧩 Template Mapping (for portfolio consistency)

- `scripts/` → `setup.sh`
- `tests/`   → `auth_test/`, `authorization_test/`, `content_test/`
- `docker/`  → `docker-compose.yml` + Dockerfiles inside each test folder
- `artifacts/` → `logs/`
- `deliverable/` → `exam_NASSOPOULOS.tar`


## ⚙️ Setup

### Requirements
- Docker
- Docker Compose v2
- Git

⚠️ **No Python virtual environment is required**.  
All dependencies are installed and executed inside Docker containers.

---

## 📦 Install Dependencies

This project relies exclusively on Docker-based execution.

### Docker Installation

#### Windows / macOS
1. Download **Docker Desktop**  
   https://www.docker.com/products/docker-desktop/

2. Install and start Docker Desktop.

3. Verify installation:
```bash
docker --version
docker compose version
```

#### Linux (Ubuntu / Debian)
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
```

(Optional – run Docker without sudo)
```bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify:
```bash
docker --version
docker compose version
```

### Notes
- Docker Compose v2 (`docker compose`) is required.
- No `venv`, `pip`, or `requirements.txt` is used.
- This guarantees reproducibility and exam compliance.

---

## 🚀 Usage

### Run the full test suite
```bash
docker compose up --build
```

### Using the helper script
```bash
bash setup.sh
```

Logs are written to:
```
logs/api_test.log
```

---

## 🐳 Docker Architecture

Each test category runs in its own container:

- `auth_test` → authentication validation
- `authorization_test` → role and permission checks
- `content_test` → protected resource access

This design ensures **strict isolation**, **reproducibility**, and **production-like validation**, aligned with MLOps best practices.

---

## 📦 Deliverable

The official exam deliverable is provided **unchanged**, as explicitly required by the certification instructions:

```
deliverable/exam_NASSOPOULOS.tar
```

---

## 🧠 Notes

- This repository reflects the **exact structure expected during the exam**.
- The deliverable archive is preserved in its original format.
- Logs and artifacts are intentionally minimal and exam-oriented.

---

## 👤 Author

Georges Nassopoulos  
📧 georges.nassopoulos@gmail.com

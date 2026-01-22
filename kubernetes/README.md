# 🚀 Kubernetes Project — FastAPI + MySQL (with Docker & DagsHub)

## 📘 Description
This project deploys a **FastAPI** application connected to a **MySQL** database inside a **Kubernetes cluster**.  
The FastAPI app is packaged as a Docker image hosted on Docker Hub:  
**`<YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi:latest`**  

It includes deployments, services, environment variables, health probes, and an optional integration test.

---

## 📁 Project Structure

```
│
├── main.py                      			## FastAPI application entrypoint
│
├── Dockerfile                   			## Docker image definition
│
├── requirements.txt             			## Python dependencies
│
├── setup.sh                     			## Interactive Kubernetes setup script around kubectl commands
│
├── deliverable/                       		## Official exam deliverable
│   └── examen_NASSOPOULOS.zip 
│
├── data/                        			## Local data directory (PV support)
│   └── .gitkeep                 
│                                
│
├── mysql/                       			## MySQL-related Kubernetes resources
│   ├── mysql-local-data-folder-pv.yaml
│   ├── mysql-service.yaml
│   └── mysql-statefulset.yaml
│
└── fastapi/                     			## FastAPI Kubernetes resources
    ├── fastapi-deployment.yaml  
    ├── fastapi-service.yaml     
    └── legacy/                  
        └── fastapi-pod.yaml     
```

---
## 🖥️ Windows & WSL2 Prerequisites

### PowerShell (Windows)

```powershell
## Check WSL installation and default version
wsl --status

## Install WSL if not already installed (admin PowerShell)
wsl --install

## List available Linux distributions
wsl --list --online

## Install Ubuntu distribution
wsl --install -d Ubuntu

## Restart terminal, then start Ubuntu (WSL)
wsl -d Ubuntu

## Check Docker Desktop installation (required for Minikube driver)
docker --version
docker compose version
```

⚠️ Docker Desktop must be running with the WSL2 backend enabled.

---

### Ubuntu (WSL) — System setup

```bash
## Update package list
sudo apt update

## Install required base tools
sudo apt install -y git curl

## Verify Git installation
git --version
```

---

### Kubernetes CLI tools (Ubuntu / WSL — binary installation)

> ⚠️ Snap is intentionally NOT used (known issues on WSL).

```bash
## Install kubectl (official binary)
curl -LO https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

## Verify kubectl installation
kubectl version --client
```

```bash
## Install Minikube (official binary)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

## Verify Minikube installation
minikube version
```

---

### Start local Kubernetes cluster (Ubuntu / WSL)

```bash
## Start Minikube using Docker Desktop as driver
minikube start --driver=docker

## Verify cluster status
kubectl get nodes
```

Expected result:
```text
minikube   Ready   control-plane   ...
```

---

### Python setup (Ubuntu / WSL)

```bash
## Check Python installation
python3 --version

## Install pip and venv if missing
sudo apt install -y python3-pip python3-venv
```


## 🧪 How to Reproduce and Test

### 1️⃣ Method 1 — Manual execution (kubectl)

```bash
## Create namespace
kubectl create namespace examen-k8s

## Deploy MySQL resources
kubectl apply -f mysql/ -n examen-k8s

## Deploy FastAPI resources
kubectl apply -f fastapi/ -n examen-k8s

## Check pods status
kubectl get pods -n examen-k8s

## Check services
kubectl get svc -n examen-k8s

## Inspect FastAPI logs
kubectl logs -n examen-k8s -l app=fastapi

## Port-forward FastAPI service
kubectl port-forward svc/fastapi-service -n examen-k8s 8000:8000

## Test application
curl http://localhost:8000/tables
```

---

### 2️⃣ Method 2 — Interactive setup script (`setup.sh`)

The `setup.sh` script provides a menu-driven alternative to manual `kubectl` commands.

```bash
chmod +x setup.sh
./setup.sh
```

Available actions:
- Create namespace
- Deploy MySQL
- Deploy FastAPI
- View pods and services
- View FastAPI logs
- Port-forward FastAPI
- Run smoke test (`/tables`)
- Cleanup (delete namespace)

---

## 🐳 Build & Push Docker Image (Docker Hub)

```bash
## Move to the project root where the Dockerfile is located
cd kubernetes

## Login to Docker Hub (required even if logged in via browser)
docker login
## Username: <YOUR_DOCKERHUB_USERNAME>
## Password: Docker Hub password or access token

## Build the Docker image locally
docker build -t <YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi:latest .

## (Optional) Tag the image with a version number
docker tag <YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi:latest \
           <YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi:1.0.0

## Push the image to Docker Hub
docker push <YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi:latest
docker push <YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi:1.0.0
```

---

## 🐳 Docker Image

| **Component** | **Value** |
|----------------|-----------|
| **Image name** | `<YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi:latest` |
| **Base image** | `python:3.10-slim` |
| **Entrypoint** | `uvicorn main:app --host 0.0.0.0 --port 8000` |
| **Registry** | https://hub.docker.com/r/<YOUR_DOCKERHUB_USERNAME>/k8s-dst-eval-fastapi |

---

## ⚙️ Environment Variables

| **Variable** | **Value** | **Description** |
|---------------|------------|----------------|
| `MYSQL_HOST` | `mysql` | MySQL service name |
| `MYSQL_PORT` | `3307` | MySQL service port |
| `MYSQL_USER` | `root` | Database user |
| `MYSQL_PASSWORD` | `RootPass123` | MySQL password |
| `MYSQL_DATABASE` | `mydb` | Database name |

---

## 🏁 Status Summary

| **Component** | **Status** | **Comment** |
|----------------|------------|-------------|
| Namespace | ✅ | `examen-k8s` created |
| MySQL | ✅ | Database `mydb`, port `3307` |
| FastAPI | ✅ | 2 replicas |
| Liveness / Readiness | ✅ | `/docs` and `/tables` OK |
| FastAPI ↔ MySQL | ✅ | Connection validated |

---

## 🌟 [OPTIONAL] Step Validated

> ✅ **Integration test: FastAPI ↔ MySQL**

- Swagger UI: `http://localhost:8000/docs`
- Endpoint tested: `GET /tables`
- Expected result:
```json
{"database": ["test_table"]}
```

## Author

Georges Nassopoulos  
Email: georges.nassopoulos@gmail.com  
Status: Educational / Exam project
---

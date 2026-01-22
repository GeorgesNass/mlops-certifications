#!/usr/bin/env bash
set -euo pipefail

## -----------------------------------------------------------------------------
## Global configuration
## -----------------------------------------------------------------------------

## Kubernetes namespace used for all resources
NAMESPACE="${NAMESPACE:-examen-k8s}"


## -----------------------------------------------------------------------------
## Utility functions
## -----------------------------------------------------------------------------

## Check if kubectl is available
require_kubectl() {
  command -v kubectl >/dev/null 2>&1 || {
    echo "ERROR: kubectl not found in PATH."
    exit 1
  }
}

## Create namespace if it does not exist
create_namespace() {
  require_kubectl
  kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1 || \
    kubectl create namespace "${NAMESPACE}"
}


## -----------------------------------------------------------------------------
## Deployment functions
## -----------------------------------------------------------------------------

## Apply MySQL Kubernetes manifests
apply_mysql() {
  create_namespace
  kubectl apply -n "${NAMESPACE}" -f mysql/
}

## Apply FastAPI Kubernetes manifests
apply_fastapi() {
  create_namespace
  kubectl apply -n "${NAMESPACE}" -f fastapi/
}


## -----------------------------------------------------------------------------
## Observability helpers
## -----------------------------------------------------------------------------

## Show pods and services status
status_all() {
  require_kubectl
  kubectl get pods -n "${NAMESPACE}" -o wide || true
  kubectl get svc -n "${NAMESPACE}" || true
}

## Show FastAPI logs
logs_fastapi() {
  require_kubectl
  kubectl logs -n "${NAMESPACE}" -l app=fastapi --tail=200 || true
}

## Port-forward FastAPI service
port_forward_fastapi() {
  require_kubectl
  kubectl port-forward -n "${NAMESPACE}" svc/fastapi-service 8000:8000
}

## Simple smoke test
smoke_test() {
  curl -sS http://localhost:8000/tables || true
  echo
}


## -----------------------------------------------------------------------------
## Cleanup
## -----------------------------------------------------------------------------

## Delete the entire namespace
cleanup() {
  require_kubectl
  kubectl delete namespace "${NAMESPACE}" --wait=true || true
}


## -----------------------------------------------------------------------------
## Interactive menu
## -----------------------------------------------------------------------------

menu() {
  echo
  echo "================ Kubernetes Setup Menu ================="
  echo "Namespace: ${NAMESPACE}"
  echo "--------------------------------------------------------"
  echo "1) Create namespace"
  echo "2) Apply MySQL"
  echo "3) Apply FastAPI"
  echo "4) Status (pods / services)"
  echo "5) Logs FastAPI"
  echo "6) Port-forward FastAPI (8000)"
  echo "7) Smoke test (/tables)"
  echo "8) Cleanup (delete namespace)"
  echo "9) Apply ALL"
  echo "0) Exit"
  echo
}

while true; do
  menu
  read -r -p "Choose: " choice
  case "${choice}" in
    1) create_namespace ;;
    2) apply_mysql ;;
    3) apply_fastapi ;;
    4) status_all ;;
    5) logs_fastapi ;;
    6) port_forward_fastapi ;;
    7) smoke_test ;;
    8) cleanup ;;
    9) apply_mysql; apply_fastapi; status_all ;;
    0) exit 0 ;;
    *) echo "Invalid choice." ;;
  esac
done

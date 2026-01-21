#!/usr/bin/env bash
## Load test script for the Accident Prediction API
## Mixes valid and invalid requests, then fetches /metrics
## Usage: ./load_test.sh

set -euo pipefail

## Base URL of the FastAPI service
API_URL="http://localhost:8000"

## Prediction endpoint
PREDICT_ENDPOINT="${API_URL}/predict/"

## Prometheus metrics endpoint
PROMETHEUS_METRICS="${API_URL}/metrics"

## Total number of requests (valid + invalid + misc)
ITERATIONS=40

## Delay between requests (seconds)
SLEEP_BETWEEN=0.05

## Valid payloads matching the Accident schema
valid_payloads=(
'{"place":1,"catu":1,"sexe":1,"secu1":2.0,"year_acc":2021,"victim_age":42,"catv":2,"obsm":0,"motor":1,"catr":3,"circ":3,"surf":1,"situ":1,"vma":90,"jour":29,"mois":11,"lum":4,"dep":80,"com":80131,"agg_":1,"int_":1,"atm":0,"col":7,"lat":49.8516,"long":2.4042,"hour":21,"nb_victim":1,"nb_vehicules":1}'
'{"place":10,"catu":3,"sexe":2,"secu1":0.0,"year_acc":2021,"victim_age":19,"catv":2,"obsm":1,"motor":1,"catr":4,"circ":2,"surf":1,"situ":1,"vma":30,"jour":4,"mois":11,"lum":5,"dep":59,"com":59350,"agg_":2,"int_":2,"atm":0,"col":6,"lat":50.6325934047,"long":3.0522062542,"hour":22,"nb_victim":4,"nb_vehicules":1}'
'{"place":1,"catu":1,"sexe":1,"secu1":2.0,"year_acc":2021,"victim_age":78,"catv":1,"obsm":2,"motor":1,"catr":3,"circ":1,"surf":1,"situ":1,"vma":50,"jour":8,"mois":7,"lum":1,"dep":58,"com":58194,"agg_":2,"int_":4,"atm":0,"col":2,"lat":46.9885,"long":3.1663,"hour":8,"nb_victim":2,"nb_vehicules":2}'
)

## Invalid payloads to trigger 422 validation errors
invalid_payloads=(
'{"place":1,"catu":1,"sexe":"oops","secu1":2.0,"year_acc":2021,"victim_age":42}'
'{"invalid_field":123,"catu":1,"sexe":1}'
'{"place":1,"catu":1,"sexe":1,"secu1":2.0,"year_acc":2021,"victim_age":"notanumber","catv":2,"obsm":0,"motor":1,"catr":3,"circ":3,"surf":1,"situ":1,"vma":90,"jour":29,"mois":11,"lum":4,"dep":80,"com":80131,"agg_":1,"int_":1,"atm":0,"col":7,"lat":49.8516,"long":2.4042,"hour":21,"nb_victim":1,"nb_vehicules":1}'
)

## Send POST request and display status code and short response preview
send_post() {
  local payload="$1"
  http_code=$(curl -s -o /tmp/last_response_body.txt -w "%{http_code}" \
    -X POST "$PREDICT_ENDPOINT" -H "Content-Type: application/json" -d "$payload" || true)
  echo "POST $PREDICT_ENDPOINT -> ${http_code}"
  head -c 300 /tmp/last_response_body.txt | sed -n '1,3p'
  echo
}

## Send GET request and display status code and short response preview
send_get() {
  local path="$1"
  http_code=$(curl -s -o /tmp/last_response_body.txt -w "%{http_code}" "$path" || true)
  echo "GET $path -> ${http_code}"
  head -c 300 /tmp/last_response_body.txt | sed -n '1,3p'
  echo
}

echo "Starting mixed load: ${ITERATIONS} requests (valid + invalid + misc)."
echo "API endpoint: ${PREDICT_ENDPOINT}"
echo

## Main load loop
for i in $(seq 1 "$ITERATIONS"); do
  r=$((RANDOM % 10))

  if [ "$r" -le 5 ]; then
    ## Mostly valid requests
    idx=$((RANDOM % ${#valid_payloads[@]}))
    send_post "${valid_payloads[$idx]}"
  elif [ "$r" -le 7 ]; then
    ## Some invalid requests
    idx=$((RANDOM % ${#invalid_payloads[@]}))
    send_post "${invalid_payloads[$idx]}"
  else
    ## Misc requests (404 / 405)
    if [ $((RANDOM % 2)) -eq 0 ]; then
      http_code=$(curl -s -o /tmp/last_response_body.txt -w "%{http_code}" \
        -X POST "${API_URL}/predicttt/" -H "Content-Type: application/json" \
        -d '{"place":1,"catu":1}' || true)
      echo "POST ${API_URL}/predicttt/ -> ${http_code}"
      head -c 300 /tmp/last_response_body.txt | sed -n '1,3p'
      echo
    else
      send_get "$PREDICT_ENDPOINT"
    fi
  fi

  ## Small delay between requests
  sleep "$SLEEP_BETWEEN"
done

echo
echo "Mixed load finished. Fetching metrics snapshot..."
echo

## Display key Prometheus metrics
curl -s "$PROMETHEUS_METRICS" | egrep \
  "^(api_predict_total|inference_time_seconds|http_requests_total|http_request_duration_seconds)" -n || true

echo
echo "Direct Prometheus query examples:"
echo "  curl 'http://localhost:9090/api/v1/query?query=api_predict_total'"
echo "  curl 'http://localhost:9090/api/v1/query?query=inference_time_seconds_count'"
echo

#!/bin/bash

echo "=================================================="
echo "FastAPI API startup script"
echo "=================================================="
echo "Tip: it is strongly recommended to run this script inside a virtual environment (virtualenv/venv)"
echo ""

## Ask the user whether they want to install dependencies
echo "Do you want to install dependencies? (YES/NO) [Y/n]"
read response
response=$(echo "$response" | tr '[:upper:]' '[:lower:]')

if [[ "$response" == "yes" || "$response" == "y" || "$response" == "oui" || "$response" == "o" ]]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    echo "Forcing the compatible pydantic version..."
    pip3 install pydantic==1.10.13
    echo "Downloading the French spaCy model..."
    python3 -m spacy download fr_core_news_sm
else
    echo "Skipping dependencies installation."
fi

## Check if a process is already using port 8000
pids=$(lsof -ti:8000)
if [ -n "$pids" ]; then
    echo ""
    echo "A process is already using port 8000 (PID: $pids)."
    echo "Do you want to stop it? (YES/NO) [Y/n]"
    read kill_it
    kill_it=$(echo "$kill_it" | tr '[:upper:]' '[:lower:]')

    if [[ "$kill_it" == "yes" || "$kill_it" == "y" || "$kill_it" == "oui" || "$kill_it" == "o" ]]; then
        kill $pids
        sleep 2
        echo "Previous process stopped."
    else
        echo "Cannot start a new server on port 8000. Reusing the existing API."
    fi

    ## Restart FastAPI server in background
    echo ""
    echo "Starting FastAPI server with uvicorn (background)..."
    nohup python3 -m uvicorn main:app --reload > uvicorn.log 2>&1 &
    sleep 5
    echo "Server started on http://127.0.0.1:8000"
else
    ## Start FastAPI server in background
    echo ""
    echo "Starting FastAPI server with uvicorn (background)..."
    nohup python3 -m uvicorn main:app --reload > uvicorn.log 2>&1 &
    sleep 5
    echo "Server started on http://127.0.0.1:8000"
fi

## Interactive menu loop
while true; do
    echo ""
    echo ""
    echo "----------------------------------------------------------------------"
    echo "Please choose an option (or type 'exit' to quit):"
    echo "1. Exploratory Data Analysis (EDA)"
    echo "2. Execute curl requests (multithread - synchronous)"
    ## echo "3. Execute curl requests (multithread - asynchronous)"
    echo "3. Run a custom curl request"
    read option

    num_lines=$(grep -cve '^\s*$' requests/requests.txt)
    mapfile -t lines < <(grep -ve '^\s*$' requests/requests.txt)
    mkdir -p results

    if [[ "$option" == "1" ]]; then
        echo "Running exploratory analysis on questions..."
        python3 src/tools/eda_questions.py

    elif [[ "$option" == "2" ]]; then
        echo "Running in synchronous mode ($num_lines requests)..."
        rm -f results/responses_synchrone.txt
        for ((i = 0; i < num_lines; i++)); do
            echo -e "\n--- Request $((i+1)) ---" >> results/responses_synchrone.txt
            eval "${lines[$i]}" -s >> results/responses_synchrone.txt 2>&1
        done
        echo "Results saved to: results/responses_synchrone.txt"

    ## elif [[ "$option" == "3" ]]; then
    ##     echo "Running in asynchronous mode ($num_lines requests)..."
    ##     mkdir -p tmp_async_responses
    ##     rm -f tmp_async_responses/req_*.txt results/responses_asynchrone.txt
    ##
    ##     for ((i = 0; i < num_lines; i++)); do
    ##         (
    ##             echo -e "--- Request $((i + 1)) ---" > tmp_async_responses/req_$i.txt
    ##             eval "${lines[$i]/curl /curl -s }" >> tmp_async_responses/req_$i.txt 2>&1
    ##         ) &
    ##     done
    ##
    ##     wait
    ##
    ##     ## Rebuild the output file in order
    ##     for ((i = 0; i < num_lines; i++)); do
    ##         cat tmp_async_responses/req_$i.txt >> results/responses_asynchrone.txt
    ##         echo -e "\n" >> results/responses_asynchrone.txt
    ##     done
    ##
    ##     rm -rf tmp_async_responses
    ##     echo "Results saved to: results/responses_asynchrone.txt"

    elif [[ "$option" == "3" ]]; then
        echo "Enter your full curl command:"
        read curl_cmd
        echo -e "\n===== Custom request output ====="
        eval "$curl_cmd"

    elif [[ "$option" == "exit" ]]; then
        echo "Closing script."
        break
    else
        echo "Invalid option. Please try again."
    fi
done
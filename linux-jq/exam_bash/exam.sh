#!/bin/bash

## Function that queries the API for GPU sales as defined in the exam statement
## and stores the results in the sales file
collect_data() {
    ## Append the scraping date
    date >> /home/ubuntu/exam_NASSOPOULOS/exam_bash/sales.txt

    ## List of GPUs to query
    cartes="rtx3060 rtx3070 rtx3080 rtx3090 rx6700"

    ## Loop over each GPU and retrieve sales data via the API
    for carte in $cartes; do
        nb_ventes=$(curl -s http://0.0.0.0:5000/$carte)
        echo "$carte:$nb_ventes" >> /home/ubuntu/exam_NASSOPOULOS/exam_bash/sales.txt
    done

    ## Empty line to separate data blocks
    echo "" >> /home/ubuntu/exam_NASSOPOULOS/exam_bash/sales.txt
}

## Function call
collect_data

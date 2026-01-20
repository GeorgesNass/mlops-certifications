#!/bin/bash

## 1. Number of attributes per document + attribute name (first 12 entries)
echo "1. Number of attributes per document + attribute name (first 12 entries)"
jq '.[] | {name, total_fields: (keys | length)}' people.json | head -n 12
echo "Command: jq '.[] | {name, total_fields: (keys | length)}' people.json | head -n 12"
echo "Answer: Each document contains 17 attributes, as observed in the output."
echo -e "\n---------------------------------\n"

## 2. Number of \"unknown\" values for the birth_year attribute
echo "2. Number of \"unknown\" values for the birth_year attribute"
jq '[.[] | select(.birth_year == "unknown")] | length' people.json | tail -n 1
echo "Command: jq '[.[] | select(.birth_year == \"unknown\")] | length' people.json | tail -n 1"
echo "Answer: There are exactly 42 characters with birth_year set to 'unknown'."
echo -e "\n---------------------------------\n"

## 3. Creation date (YYYY-MM-DD format) and name (first 10 entries)
echo "3. Creation date (YYYY-MM-DD format) and name (first 10 entries)"
jq '.[] | {name, creation_date: (.created | split("T")[0])}' people.json | head -n 10
echo "Command: jq '.[] | {name, creation_date: (.created | split(\"T\")[0])}' people.json | head -n 10"
echo -e "\n---------------------------------\n"

## 4. Pairs of character IDs born in the same year
echo "4. Pairs of character IDs born in the same year"
jq '[ group_by(.birth_year)[] | select(length == 2) | map(.url | capture("people/(?<id>[0-9]+)").id) ]' people.json
echo "Command: jq '[ group_by(.birth_year)[] | select(length == 2) | map(.url | capture(\"people/(?<id>[0-9]+)\").id) ]' people.json"
echo "Answer: Several pairs share the same birth_year. Here, 6 pairs are identified."
echo -e "\n---------------------------------\n"

## 5. First movie of each character with their name (first 10 entries)
echo "5. First movie of each character with their name (first 10 entries)"
jq '.[] | try {name, first_film: (.films[0])} catch {name, first_film: "not_available"}' people.json | head -n 10
echo "Command: jq '.[] | try {name, first_film: (.films[0])} catch {name, first_film: \"not_available\"}' people.json | head -n 10"
echo -e "\n---------------------------------\n"

## BONUS SECTION
echo -e "\n----------------BONUS----------------\n"

## Create bonus directory if it does not exist
mkdir -p bonus

## Bonus 6 – Remove documents where height is not numeric
jq '[.[] | if (.height | test("^[0-9]+$")) then . else empty end]' people.json > bonus/people_6.json

## Bonus 7 – Convert height to integer
jq '[.[] | select(.height | test("^[0-9]+$")) | .height |= tonumber]' people.json > bonus/people_7.json

## Bonus 8 – Characters between 156 and 171 cm
jq '[.[] | select(.height | test("^[0-9]+$")) | .height |= tonumber | select(.height >= 156 and .height <= 171)]' people.json > bonus/people_8.json

## Bonus 9 – Shortest individual among those between 156 and 171 cm
jq -r 'min_by(.height) | "\(.name) is \(.height) tall"' bonus/people_8.json > bonus/people_9.txt

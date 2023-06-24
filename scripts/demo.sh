#!/bin/bash


# Demo script
# .
# .
# .
# TBH, it's a naive testing script just to make sure everything is working :)


commands="
football competition PL
football competition PL standings --season 2022
football competition PL scorers --top 5 --season 2022
football competition PL teams --season 2021
football competition PL matches --season 2022 --matchday 38
football competition PL matches --season 2019 --matchday 1
football competition ELC matches --season 2022 --stage PLAYOFFS

echo 'Waiting 1 minute in order not to hit request limit (10 requests per minute)' && sleep 60

football competition CL standings
football competition CL matches --group A --matchday 1 --season 2022
football competition CL matches --stage SEMI_FINALS --stage final --season 2022
football competition WC matches --season 2022

football team FCB
football team MCI matches --last 5 --home --show-id
football team BOT matches --last
football team BOT matches --next

echo 'Waiting 1 minute in order not to hit request limit (10 requests per minute)' && sleep 60

football matches --date today
football matches --live
football matches --time-frame 2023-05-26 2023-06-03 --competitions PL,PD,SA,BL1,FL1
football matches --time-frame -3 4
football matches --time-frame 0 10
football matches --time-frame -3 2023-06-30
football matches --time-frame 2 1
football matches --time-frame 2023-01-01 2022-12-31
football matches --h2h 416474
football matches --h2h 418869 --last 5
football matches --h2h 416066 --last 1
"

IFS="
"
for cmd in $commands; do
    echo ">> $cmd"
    eval $cmd
    echo
done

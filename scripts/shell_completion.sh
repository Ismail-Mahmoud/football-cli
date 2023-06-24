#!/bin/bash

# This script enables shell completion
# by generating a script and sourcing it in your shell config file.
# This only works for bash, zsh and fish.
# To add support for your shell, please check the following link:
# https://click.palletsprojects.com/en/8.1.x/shell-completion/#adding-support-for-a-shell


if [[ $# -eq 0 ]]; then
    echo "Missing argument. Please provide your shell name."
    exit 2
fi

if [[ $# -gt 1 ]]; then
    echo "Too many arguments."
    exit 2
fi

shell=$1

if [[ $shell == "bash" || $shell == "zsh" ]]; then
    completion_script=~/.football_complete.$shell
    rc_file=~/."$shell"rc

    _FOOTBALL_COMPLETE="$shell"_source football > $completion_script
    echo "Completion script generated and saved to $completion_script"

    echo "# football-cli completion" >> $rc_file
    echo "source $completion_script" >> $rc_file
    echo "Completion script sourced in $rc_file"

elif [[ $shell == "fish" ]]; then
    completion_script=~/.config/fish/completions/football.fish
    _FOOTBALL_COMPLETE="$shell"_source football > $completion_script
    echo "Completion script generated and saved to $completion_script"

else
    echo "Completion is only supported for the following shells: (bash, zsh, fish)."
fi

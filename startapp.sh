#!/bin/bash
# This script serves as the main entry point for the app

# Help message
usage='
This script is the main interface to the multiplayer back-end.
Options:
    -h, --help      Print this help page.
    -t, --test      Run PEP8 linter and unit tests.
    -d, --debug     Export DEBUG environment variable before running.
'

# Get console width
cols=$(tput cols)

runTests() {
    cd src/
    printHeadline 'PEP8 Linting'
    flake8

    if [[ $? -eq 0 ]]; then
        printHeadline green 'no linting errors'
    else
        printHeadline red 'linting failed'
    fi

    python -m pytest
}

# print headline with text. Optional first argument determines color.
printHeadline() {
    # use green/red text if first argumnet is 'green' or 'red'
    if [[ $1 = green ]]; then
        printf '\e[32m'
        shift
    elif [[ $1 = red ]]; then
        printf '\e[31m'
        shift
    fi
    printf '\e[1m'
    wordlength=${#1}
    padlength=$(( ($cols - $wordlength - 2) / 2 ))
    printf %"$padlength"s | tr " " "="
    printf " $1 "
    printf %"$padlength"s | tr " " "="
    printf '\e[0m\n'
}

# print line with terminal width
printline() {
    printf '\e[1m'
    printf %"$cols"s | tr " " "-"
    printf '\e[0m\n'
}

debugMode() {
    export DEBUG=true;
    printHeadline red 'Debug Mode';
    echo 'environment variable "DEBUG" exported'
}

# parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h | --help)        echo "$usage";
                            exit 0;;
        -t | --test)        runTests;
                            exit 0;;
        -d | --debug)       debugMode;
                            shift ;;
        *)                  echo "Unexpected option $1, use -h for help";
                            exit 1;;
    esac
done


# Print some info
printHeadline 'Teknisk Museum Mulitplayer'
printf "$(python --version) \n$(which python) \n"
printline

# Launch app
cd src
echo "Launching eventlet server"
python3 -m webapp.app

printline

#!/bin/bash
# This script serves as the main interface to the app

# File paths
appname='mulitplayer'
logfile="/home/LogFiles/${appname}.log"
tmppath="/tmp/${appname}/workers.pid"


# Compute number of workers
ncores=$(nproc)
nworkers=$(((2*$ncores)+1))
if [[ $nworkers -gt 12 ]]; then
    nworkers=12
fi

# Get console width for printing
cols=$(tput cols)


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

killProcesses() {
    tempfile="$tmppath"
    if [[ $1 = "silent" ]]; then
        silent=true
    fi

    if [[ -f "$tempfile" ]]; then
        kill $(cat $tempfile)
        ! $silent && echo "processes eliminated"
        rm $tempfile
    else
        ! $silent && echo "no PID file found, exiting"
    fi
}

printHelp() {
# Help string
    usage="Script to start ${appname}.
    Options:
    -h, --help      Print this help page.
    -k, --kill      Kill running workers.
    -i, --install   Install python dependencies and make temp directory.
    -w, --workers   Specify number workers."
    echo "$usage"
}

installApp() {
    printHeadline 'installing dependencies'
    pip install -r requirements.txt
    mkdir "/tmp/${appname}"
    printline
}

# Parse flags
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -k | --kill)        killProcesses;
                            exit;;
        -h | --help)        printHelp;
                            exit;;
        -i | --install)     installApp; 
                            exit;;
        -w=* | --workers=*) nworkers="${1#*=}";
                            shift ;;
        *)                  echo "Unexpected option: $1, use -h for help";
                            exit 1 ;;
    esac
done


# Print some info
printHeadline "Teknisk museum $appname"
echo "$(python --version)
$(which python)
Number processing units: $ncores
Number of workers: $nworkers"

printline

for (( i=1; i <= $nworkers; i++)); do
    python src/app.py &
    workers[$i]=$!
    printf "Spawning worker %02d PID: %04d \n" $i $!
done

# kill old processes if excisting
killProcesses silent

# write pids to pidfile in /tmp/
printf "PIDs stored in: \n${tmppath}\n"
echo "${workers[@]}" > "$tmppath"

printline

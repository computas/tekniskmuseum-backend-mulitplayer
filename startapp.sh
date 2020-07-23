# Parse flags
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d | --debug)       debug=true;
                            nworkers=1;
                            shift ;;
    esac
done

if [[ $debug = true ]]; then
    export DEBUG=true
fi
cd src
clear
gunicorn --bind=0.0.0.0 --worker-class eventlet -w 1 webapp.api:app

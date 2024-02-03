#!/usr/bin/bash

set -e

DEVELOPMENT=false

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        -d|--devel|--development)
            DEVELOPMENT=true
            shift
            ;;
        *)
            echo "Unknown option: $key"
            exit 1
            ;;
    esac
done

# wait for Postgres to start
function postgres_ready(){
python << EOF
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="$POSTGRES_DB", user="$POSTGRES_USER", password="$POSTGRES_PASSWORD", host="$POSTGRES_HOST", port="$POSTGRES_PORT")
except psycopg2.OperationalError:
    sys.exit(-1)
else:
    conn.close()
sys.exit(0)
EOF
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Running migrations"
flask db upgrade
echo "creating admin user"
flask users create-admin

if [ "$DEVELOPMENT" = true ]; then
    echo "Starting development server"
    exit $(flask --app web run --host=0.0.0.0 --port 8000 --debug)
    
fi

echo "Starting gunicorn server"
gunicorn -w 2 'web:create_app()' -b 0.0.0.0:8000 --reload
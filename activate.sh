#!/bin/bash
source venv/bin/activate

if [ -f .env ]; then
    set -a
    source .env
    set +a
fi


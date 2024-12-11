#!/bin/bash

# if arg is passed, use it as the LLM_MODEL
# otherwise log out fallback value

function print_usage() {
    echo "Usage: $0 <LLM_MODEL> <CREDENTIALS_FILE>"
    echo "LLM_MODEL: The LLM model to use"
    echo "CREDENTIALS_FILE: The path to the credentials file"
}

if [ -n "$1" ]; then
    export LLM_MODEL=$1
else
    print_usage
    exit 1
fi

if [ -n "$2" ]; then
    export CREDENTIALS_FILE=$2
else
    echo "CREDENTIALS_FILE is not set, failing"
    print_usage
    exit 1
fi

# Deploy using Ansible
echo "Deploying with Ansible..."
cd src/ansible
ansible-playbook site.yml
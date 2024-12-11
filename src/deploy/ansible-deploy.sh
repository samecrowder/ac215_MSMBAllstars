#!/bin/bash

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

# this should be run from the project root
PROJECT_ROOT_ABSOLUTE_PATH=$(pwd)
cd src/ansible

if [ -n "$2" ]; then
    CREDENTIALS_FILE="$2"
    # try reading the path as given; if it works, it is an absolute path
    if [ -f "$CREDENTIALS_FILE" ]; then
        echo "Credentials file exists at absolute path $CREDENTIALS_FILE"
    else
        # the path as it is given is relative to the project root; convert to absolute path
        CREDENTIALS_FILE="$PROJECT_ROOT_ABSOLUTE_PATH/$CREDENTIALS_FILE"
        # ensure that a credentials file exists here
        if [ ! -f "$CREDENTIALS_FILE" ]; then
            echo "Credentials file does not exist at $CREDENTIALS_FILE, failing"
            print_usage
            exit 1
        else 
            echo "Credentials file exists at new absolute path $CREDENTIALS_FILE"
        fi
    fi

    # Export the absolute path
    export CREDENTIALS_FILE
else
    echo "CREDENTIALS_FILE is not set, failing"
    print_usage
    exit 1
fi

echo "Reading credentials file from $CREDENTIALS_FILE"

# Change to project root and use absolute path for credentials
cd $PROJECT_ROOT_ABSOLUTE_PATH
echo "Deploying with Ansible from $(pwd)..."
ansible-playbook src/ansible/site.yml

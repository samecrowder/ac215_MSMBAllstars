#!/bin/bash

# if arg is passed, use it as the LLM_MODEL
# otherwise log out fallback value
if [ -n "$1" ]; then
    LLM_MODEL=$1
else
    echo "LLM_MODEL is not set, failing"
    exit 1
fi

# Deploy using Ansible
echo "Deploying with Ansible..."
cd src/ansible
ansible-playbook site.yml
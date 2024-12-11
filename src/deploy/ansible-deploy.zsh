#!/usr/bin/env zsh

# Deploy using Ansible
echo "Deploying with Ansible..."
cd src/ansible
ansible-playbook site.yml
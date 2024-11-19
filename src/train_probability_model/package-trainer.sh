#!/bin/bash

# Build the trainer package
cd package
python setup.py sdist bdist_wheel

# Create the trainer archive
cd ..
rm -rf dist
mkdir -p dist
tar -zcvf dist/tennis-trainer.tar.gz package/

# Upload to GCS
gsutil cp dist/tennis-trainer.tar.gz gs://msmballstars-data/train_tar/
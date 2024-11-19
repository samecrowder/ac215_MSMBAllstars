#!/bin/bash

# Define GCS bucket URI
export GCS_BUCKET_URI="gs://msmballstars-data/train_tar"

# Clean up any existing archives
rm -f trainer.tar trainer.tar.gz

# Create a new tar archive of the package directory
tar cvf trainer.tar package

# Compress the tar file
gzip trainer.tar

# Copy to GCS
gsutil cp trainer.tar.gz $GCS_BUCKET_URI/tennis-trainer.tar.gz
echo "Trainer package uploaded to $GCS_BUCKET_URI/tennis-trainer.tar.gz"
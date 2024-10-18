AC215 - Milestone 2 (MSMBAllstars)
==============================
**Team Members**

- Itamar Belson
- Kenny Chen
- Sam Crowder
- Clay Coleman

**Group Name**

MSMBAllstars

**Project**

The goal of this project is to develop a machine learning application that accurately predicts the outcome of a tennis match given a handful of inputs about the matchup.
We plan to use a recurrent architecture (e.g. LSTM) trained on an autoregressive format of the underlying data, as in train on match i to j for player 1 and similarly for player 2, (using the same LSTM block across two players)  join the two hidden state outputs at j, and predict probability of winning in match j+1 where player 1 and player 2 will play (where i <= j).

### Milestone 2 ###

We'll primarily use a dataset available on GitHub of all ATP matches over the last several decades, presented in CSV format. This dataset can be viewed here: https://github.com/JeffSackmann/tennis_atp/tree/master.

Project Organization
------------
      ├── LICENSE
      ├── README.md
      ├── notebooks
      ├── references
      ├── setup.py
      ├── reports
      └── src
            ├── preprocessing
                ├── Dockerfile
                ├── docker-shell.sh
                ├── preprocess.py
                ├── Pipfile
                └── Pipfile.lock
            ├── api
                ├── Dockerfile
                ├── docker-shell.sh
                ├── app.py
                ├── Pipfile
                └── Pipfile.lock
            ├── llm
                ├── Dockerfile
                ├── docker-shell.sh
                ├── app.py
                ├── Pipfile
                └── Pipfile.lock

Preprocess container
------------
- Required inputs: GCS Project Name and GCS Bucket Name.
- Output: Processed data stored in the GCS Bucket.

(1) `src/preprocessing/preprocess.py`: This file manages the preprocessing of our dataset.

(2) `src/preprocessing/Pipfile`: Lists the Python packages essential for image preprocessing.

(3) `src/preprocessing/Dockerfile`: The Dockerfile is configured to use `python:3.9-slim-buster`. It sets up volumes and uses secret keys (which should not be uploaded to GitHub) for connecting to the GCS Bucket.

### Running the preprocessing container
**Setup GCP Service Account**
1. Create a secrets folder that is on the same level as the project folder.
2. Head to [GCP Console](https://console.cloud.google.com/home/dashboard).
3. Search for "Service Accounts" from the top search box OR go to: "IAM & Admins" > "Service Accounts" and create a new service account called "MSMBAllstars".
4. For "Grant this service account access to project", and give the account the following three permissions:
      - "Cloud Storage" > "Storage Object Viewer"
      - "Cloud Storage" > "Storage Object User"
      - "Cloud Storage" > "Storage Object Creator"
5. Click done. This will create a service account.
6. Click on the "..." under the "Actions" column and select "Manage keys".
7. Click on "ADD KEY" > "Create new key" with "Key type" as JSON.
8. Copy this JSON file into the secrets folder created in step 1 and rename it as "data-service-account.json".

**Setup GCS Bucket**
1. Head to [GCP Console](https://console.cloud.google.com/home/dashboard).
2. Search for "Buckets" from the top search box OR go to: "Cloud Storage" > "Buckets" and create a new bucket with an appropriate bucket name e.g. "msmballstars-test".
3. Click done. This will create a new GCS Bucket.

**Add Raw Data to GCS Bucket**
1. In the new GCS Bucket, create a folder called "raw_data".
2. Upload all of the atp_matches_<year>.csv files from https://github.com/JeffSackmann/tennis_atp/tree/master into the "raw_data" folder.

**Set GCP Credentials**
1. Head to src/preprocessing/docker-shell.sh.
2. Replace `GCS_BUCKET_NAME` and `GCP_PROJECT` with corresponding GCS Bucket Name that you have chosen above and GCP Project Name.

**Execute Dockerfile**
1. Execute `docker-shell.sh` from its directory to build and run the docker container.
2. Upon completion, your GCS Bucket should display the processed data as shown under the default folder name "version1".
![bucket-data](assets/bucket-data.png)

API container
------------
**Execute Dockerfile**
1. Execute `docker-shell.sh` from its directory to build and run the docker container. This should start a FastAPI server at `http://127.0.0.1:8000`.


Probability Model container
------------
**Execute Dockerfile**
1. Execute `docker-shell.sh` from its directory to build and run the docker container. This should start a FastAPI server at `http://127.0.0.1:8001`.


LLM container
------------
**Execute Dockerfile**
1. Execute `docker-shell.sh` from its directory to build and run the docker container. This should start a FastAPI server at `http://127.0.0.1:8002`.

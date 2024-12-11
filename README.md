# AC215 - Milestone 5 (MSMBAllstars)

**Team Members**

- Itamar Belson
- Kenny Chen
- Sam Crowder
- Clay Coleman

**Group Name**

MSMBAllstars

## Project Overview

Our project develops a machine learning application that predicts tennis match outcomes using historical ATP match data. The system combines an LSTM-based prediction model with an LLM-powered chat interface for user interaction.

### Milestone 5 - Kubernetes Deployment & GPU Acceleration & ML Pipeline

For this milestone, we've implemented a robust Kubernetes deployment on Google Cloud Platform (GCP) with the following key features:

1. **Kubernetes Cluster Architecture**

   - Multi-node GKE cluster with both CPU and GPU nodes
   - GPU node pool using NVIDIA L4 GPUs for LLM acceleration
   - Load balancing and auto-scaling capabilities
   - Resource optimization across nodes

2. **Service Components**

   - API Service (FastAPI)
   - Probability Model Service (Tennis prediction model)
   - LLM Service (Chat interface)
   - Ollama Service (GPU-accelerated LLM model)

3. **Infrastructure as Code**

   - Ansible-based deployment automation
   - Kubernetes manifests for all services
   - GPU resource management and scheduling
   - Container orchestration and scaling

4. **GPU Acceleration**
   - NVIDIA device plugin integration
   - GPU-optimized Ollama container
   - Efficient resource allocation for ML workloads

5. **ML Pipeline**
   - Single pipeline for preprocessing (see `run_pipeline.sh` in root)
   - Trianing on GCP Vertex AI and sweep optimization on Weights & Biases
   - Deployment of model only if passes validation metric threshold

## System Architecture

![System Overview](deliverables/diagrams/solution_architecture.png)

## Deployment Architecture

The system is deployed on GKE with the following node configuration:

- 3 CPU nodes (e2-medium) for general workloads
- 1 GPU node (g2-standard-4) with NVIDIA L4 for LLM acceleration

### Node Pool Configuration

```bash
# CPU Node Pool
gcloud container node-pools create default-pool \
    --machine-type=e2-medium \
    --num-nodes=3

# GPU Node Pool
gcloud container node-pools create l4-gpu-pool \
    --machine-type=g2-standard-4 \
    --accelerator type=nvidia-l4,count=1 \
    --num-nodes=1
```

## Deployment Process

1. **Setup GCP Project**

```bash
# Set project ID
export PROJECT_ID="tennis-match-predictor"
gcloud config set project $PROJECT_ID
```

2. **Create GKE Cluster**

```bash
gcloud container clusters create tennis-predictor-cluster \
    --zone us-central1-a \
    --machine-type g2-standard-4
```

3. **Deploy with Ansible**

```bash
cd src/ansible
ansible-playbook deploy-k8s.yml
```

4. **Verify Deployment**

```bash
kubectl get pods -o wide
kubectl get services
```

## Service Endpoints

The application exposes the following endpoints:

- **API Service**: `http://<external-ip>:8000`

  - `/predict` - Match prediction endpoint
  - `/chat` - WebSocket chat endpoint

- **Probability Model**: Internal service on port 8001
- **LLM Service**: Internal service on port 8002
- **Ollama Service**: Internal service on port 11434

## Monitoring and Maintenance

1. **Check GPU Status**

```bash
kubectl describe node <gpu-node-name> | grep nvidia
```

2. **View Service Logs**

```bash
kubectl logs -f deployment/api
kubectl logs -f deployment/ollama
```

3. **Monitor Resources**

```bash
kubectl top nodes
kubectl top pods
```

## Testing

To test the deployed services:

1. **Prediction API**

```bash
curl -X POST "http://<external-ip>:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "player_a_id": "Novak Djokovic",
    "player_b_id": "Roger Federer",
    "lookback": 10
  }'
```

2. **Chat API**

```bash
curl -X POST "http://<external-ip>:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who is more likely to win between Federer and Nadal?",
    "history": []
  }'
```

## Project Organization

    ├── README.md
    ├── src
        ├── ansible/                    # Ansible deployment configuration
        │   ├── inventory/
        │   ├── roles/
        │   └── deploy-k8s.yml
        ├── api/                        # FastAPI application
        ├── llm/                        # LLM service
        ├── probability_model/          # Tennis prediction model
        └── ollama/                     # GPU-accelerated LLM container

## Future Improvements

1. Implement horizontal pod autoscaling (HPA)
2. Add monitoring with Prometheus and Grafana
3. Implement CI/CD pipeline for automated deployments
4. Add backup and disaster recovery procedures

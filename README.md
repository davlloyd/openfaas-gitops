# openfaas-gitops
Project to drive a GitOps process linking Git, vSphere and Slack with OpenFaaS 

## Installation
1. Create Kubernetes Secrets for integration point: Slack and vSphere.
2. Create webhook for githup repository
3. Deploy Openfaas vCenter Connector in a network location which has access to vCenter and OpenFaaS Gateway
4. Deploy Gitops functions via Faas-cli up

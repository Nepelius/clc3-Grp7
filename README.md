# CLC3 Group 7 - Monitoring with Prometheus and Grafana
## Setup
### Docker
We created a Dockerfile that can be used to build a Dockerimage. Port-forwarding for the container is needed in order to access the Prometheus and Grafana Dashboards
```
docker build .
docker run -it -p 9090:9090 <image_name>
```

### Kubernetes Cluster with AKS

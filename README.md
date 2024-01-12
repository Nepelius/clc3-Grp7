# CLC3 Group 7 - Monitoring with Prometheus and Grafana
## Setup
### Docker
We created a Dockerfile that can be used to build a Dockerimage. Port-forwarding for the container is needed in order to access the Prometheus and Grafana Dashboards
```
docker build .
docker run -it -p 9090:9090 <image_name> /bin/sh
```

### AKS setup
First, you have to login with your Azure account
```
az login
```
Next, set your Subscription and download your credentials
```
az account set --subscription <subscription_name>
az aks get-credentials --resource-group <rg_name> --name <cluster_name>
```
### Installing Prometheus and Grafana via Helm
Now we can execute a single command which installs Prometheus and Grafana via Helm Chart. Before that, let's create a namespace for the monitoring ressources
```
kubectl create ns monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring
```
After this, all pods, services and other ressources related to Prometheus and Grafana are deployed. By executing ```kubectl get all``` you can list all installed ressources.

### Port forwarding
To access the Prometheus Dashboard, following port-forward is used
```
kubectl port-forward -n monitoring pod/prometheus-monitoring-kube-prometheus-prometheus-0 9090
```
Attention: The name of the pod could be slightly different depending on the deployment name you chose.

Access Grafana Dashboard
```
kubectl port-forward -n monitoring pod/monitoring-grafana-6c7d669584-nqjk4 3000
```
Attention: Pod name might be slightly different
In order to login to the Grafana Dashboard, use default username ```admin``` and password ```prom-operator```.

### MongoDB
First, the bitnami packaged mongoDB helm chart is installed
```
helm install my-release oci://REGISTRY_NAME/REPOSITORY_NAME/mongodb
```

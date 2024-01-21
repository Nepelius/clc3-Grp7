# CLC3 Group 7 - Monitoring with Prometheus and Grafana
## Organizational
### Introduction

### Responibilites
The responsibility changed since our proposal.

* 

### Kubernetes Namespace overview
```
└── namespaces
    ├── monitoring
    └── mongodb
```
The ```monitoring``` namespace is responsible for Prometheus and Grafana, while all ressources of the MongoDB service and MongoDB app are stored within ```mongodb```.

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
After this, all pods, services and other ressources related to Prometheus and Grafana are deployed. By executing ```kubectl -n monitoring get all``` you can list all installed ressources.

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
**Attention**: Pod name might be slightly different.
In order to login to the Grafana Dashboard, use default username ```admin``` and password ```prom-operator```.

### MongoDB
First, a new namespace called mongodb and the bitnami packaged mongoDB helm chart is installed
```
kubectl create ns mongodb
helm install mongodb oci://registry-1.docker.io/bitnamicharts/mongodb -n mongodb
```
After installing, the port of the mongoDB service can be forwarded to access from outside the cluster on port 27017
```
kubectl port-forward --namespace mongodb svc/mongodb 27017:27017
```
In order to login to the database, you need to specify the username=```root``` and the password you get by executing the following commands
```
export MONGODB_ROOT_PASSWORD=$(kubectl get secret --namespace mongodb mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 -d)
echo $MONGODB_ROOT_PASSWORD
```
To actually access the database, you can install the [MongoDB Compass](https://www.mongodb.com/try/download/compass) application on your desktop environment and connect to the exposed port. When entering a new connection go to "Advanced Connection Options", "Authentication", "Username/Password" and enter your credentials.

![MongoDB Compass](images/compass.JPG)

### MongoDB App

A custom REST api app with python was delevolped inside the [mongodb_app](mongodb_app) folder. In order to deploy the app to the kubernetes cluster, following steps have to be done, beginning with creating the Docker image. Open a terminal inside the [mongodb_app](mongodb_app) folder.
```
docker build -t <docker_hub_username>/mongodb-app:0.0.1 .
```
This will build a docker image with python and all dependencies installed. Now we push this image to DockerHub in order to connect it with kubernetes.
```
docker push <docker_hub_username>/mongodb-app:0.0.1
```
**Attention**: You have to change the image name specified in [deployment.yaml](mongodb_app/deployment.yaml) to ```<docker_hub_username>/mongodb-app:0.0.1```. Additionally, please change the MongoDB username and password in the ```env``` section.
Next, you can deploy the app to the kubernetes cluster.
```
kubectl apply -f deployment.yaml -n mongodb
```
After a few minutes when executing ```kubectl get pods -n mongodb```, you should see the status of the mongodb-app as READY. If that is not the case, you probably spelled the image name wrong in [deployment.yaml](mongodb_app/deployment.yaml) or when executing the command.

The app should be ready now, check this by executing a port forward.
```
kubectl port-forward service/mongodb-app 5000 -n mongodb
```
By opening "http://localhost:5000" in the browser, you should see the welcome message. On "http://localhost:5000/notes" all entries in the MongoDB database are listed.

With an API tool like Insomnia, POST, DELET and GET requests can be sent to the MongoDB API app on port 5000.
The following image shows the creation of a new note entry in the "notes" MongoDB database:

![create note](images/create_note.JPG)

Additionaly, note entries can be deleted by making a DELETE request. All entries with the specified name will be deleted.

![delete notes](images/delete_notes.JPG)

**Note**: POST and DELETE methods are located at localhost:5000/notes.
Finally, when visiting the site localhost:5000/notes in the browser, all stored note entries are displayed.
When visiting localhost:5000/notes/<name>, a filter on the person specified can be viewed:

![get filter](images/get_filter.JPG)

### Activate prometheus-mongodb-exporter
First download mongodb-exporter and unzip it. (in our case, we created a directory beforehand where we downloaded it to)
```
wget https://github.com/percona/mongodb_exporter/releases/download/v0.40.0/mongodb_exporter-0.40.0.linux-amd64.tar.gz
tar xvzf mongodb_exporter-0.40.0.linux-amd64.tar.gz
```

The prometheus-mongodb-exporter chart is usually not activated to activate it the possible values to change can be checked by printing the values.yaml file from the chart into a new file called [mongodb.yaml](mongodb.yaml).
```
helm show values prometheus-community/prometheus-mongodb-exporter > mongodb.yaml
```
There is also the possiblity of installing mongodb-exporter if it is not installed yet, but this was not tested in our case.
Only a few lines have to be changed in the YAML file, therfore everything in here can be deleted and the following lines inserted.
```
mongodb:
  uri: "mongodb://<user>:<password>@mongodb.mongodb.svc.cluster.local:27017"

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "9216"
  prometheus.io/path: /metrics

serviceMonitor:
  enabled: true
  interval: 20s
  namespace:
  additionalLabels:
    release: monitoring
```
Now the chart can be installed in a new release (important to not use the same release **"monitoring"** as before, otherwise the release will be overwritten). The changed mongodb.yaml file will be used to activate the service and pod.
```
helm install mongo-export prometheus-community/prometheus-mongodb-exporter --values=mongodb.yaml -n monitoring
```

![MongoDB Service](images/mongodb_service.PNG)

If this port is now forwarded the new metrics from MongoDB can be viewed there.
```
kubectl port-forward service/mongo-export-prometheus-mongodb-exporter 9216 -n monitoring
```

![MongoDB Metrics](images/mongodb_metrics.PNG)

Additionally, the serviceMonitor is now in the "Targets" Tab on Prometheus [http://localhost:9090/targets]

![MongoDB Target](images/mongodb_target.PNG)

### Add a new rule


### Setup Slack workspace and channel
Create a new Slack workspace and a channel where the alerts should be posted to.
First a new Webhook will be added by adding a new app.
![MongoDB Metrics](images/1_slack_add_app.PNG)

Look for "Incoming Webhook" or "Eingehende Webhooks" in german.

![MongoDB Metrics](images/2_slack_add_webhook.PNG)

Select the channel where the alert should be posted to.

![MongoDB Metrics](images/3_slack_select_channel.PNG)

A new webhook URL will be created, which has to be saved to later add to the alertmanager.

![MongoDB Metrics](images/4_slack_url.PNG)

### Setup alertmanager for Slack
To change the alertmanager create a file [alertmanager.yaml](alertmanager.yaml) with following content.
With the addition of the webhook url the alerts will now be sent to the selected Slack channel. Additionally, some formatting was added for the alert.
```
alertmanager:
  config:
    global:
      resolve_timeout: 2m
      slack_api_url: <webhook url>
    route:
      group_by: ['namespace']
      group_wait: 30s
      group_interval: 2m
      repeat_interval: 5m
      receiver: 'slack-notifications'
    receivers:
    - name: 'slack-notifications'
      slack_configs:
        - channel: '#<channel name>'
          send_resolved: true
          icon_url: https://avatars3.githubusercontent.com/u/3380462
          title: |-
           [{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] {{ .CommonLabels.alertname }} for {{ .CommonLabels.job }}
           {{- if gt (len .CommonLabels) (len .GroupLabels) -}}
             {{" "}}(
             {{- with .CommonLabels.Remove .GroupLabels.Names }}
               {{- range $index, $label := .SortedPairs -}}
                 {{ if $index }}, {{ end }}
                 {{- $label.Name }}="{{ $label.Value -}}"
               {{- end }}
             {{- end -}}
             )
           {{- end }}
          text: >-
           {{ range .Alerts -}}
           *Alert:* {{ .Annotations.title }}{{ if .Labels.severity }} - `{{ .Labels.severity }}`{{ end }}
      
           *Description:* {{ .Annotations.description }}
      
           *Details:*
             {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
             {{ end }}
           {{ end }}
```

Upgrade the **prometheus-community/kube-prometheus-stack** chart with the **"monitoring"** release.
```
helm upgrade monitoring prometheus-community/kube-prometheus-stack --values=alertmanager.yaml -n monitoring
```

## Grafana
(As previously mentioned, use to access the Grafana Dashboard via
```
kubectl port-forward -n monitoring pod/monitoring-grafana-6c7d669584-nqjk4 3000
```
**Attention**: Pod name might be slightly different.
In order to login to the Grafana Dashboard, use default username ```admin``` and password ```prom-operator```.)

### Connect to Prometheus
In order to visualize our metrics, click "Data sources" in the menu on the upper left:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/26db1eae-a922-4bc6-9c11-12847ab812a3)

Now click "Add a new data source" and choose "Prometheus".
Then, connect with the Prometheus server url and save the data source:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/135f9a39-e891-443f-8ef3-b3761f55362a)

### Build a Dashboard
To create a dashboard, the menu can be navigated to "Dashboards":

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/33b5c559-efe2-4d69-b911-4b76485cd3dd)

After clicking "New" one can import an existing dashboard to build upon from https://grafana.com/grafana/dashboards/:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/5e26a147-7d1d-44f2-81e9-4e13b74ab854)

We choose the "Prometheus 2.0 Overview" dashboard: https://grafana.com/grafana/dashboards/3662-prometheus-2-0-overview/ and set our data source after loading it via id:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/8c8611bd-df4e-4ede-99cf-c2239255e138)


After opening the dashboard, new visualizations can be added with the button on the upper right: 

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/91c5c83c-5732-47d4-8265-d600e0a48b25)

We first added a metric, filtered and set the minimum stepsize to one. After pressing "run queries" a graph is created:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/e2f0c084-bd7d-46d1-85a3-75696db213f0)


On the right, one can choose the type and the visuals of the graph, e.g. toggling the Legend visibility:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/1f013407-8600-44a7-81f5-8cd3d02f2bfc)

### Alerts
Grafana can also add alerts the the graphs: 

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/d681e171-1e82-40e6-8d5f-6e3d1cdd9854)

To create an alert that fires if the amount of objects rises above 5, a reduce function and a threshold is required:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/a85a55fd-0d36-4cc1-b036-b85530a5530f)

The alert additionally has to be stored in a folder and added to an evalaluation group and can then be saved:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/758058a9-2c3b-435e-bf11-88e0633ee8d4)

The results (after changing some visuals like the color palette) look like this:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/e8a0375b-73c6-4d30-9569-ad1495a95392)

### Transformations
The data can also be transformed. 

We created a new graph: the metrics stayed the same as before but the graph type was changed to "Table":

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/8e37922f-0e60-445d-8a46-072eb31e6347)

To show the highest 10 amount of objects and their latest timestamps, the timestamps were formated, grouped, sorted and limited:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/a6155e85-0604-40a2-bf08-2dbf2b446a2c)



The menu on the right was used to enable filters and lookup menus (via hovering a data point) as well as the design changes including pages:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/fd9906dc-7a15-4484-be3c-8262713dab9c)

### Results
A few graphs later, our end result looks like this:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/856f7ec5-d4e4-42db-8345-d3c7969becf8)


Thanks to the template we used, there are additional metrics like Uptime, Memory Chunks, Upness and a graph how many series are created and deleted over time:

![image](https://github.com/Nepelius/clc3-Grp7/assets/151569651/e85379e2-9c99-4c09-83d3-00f03f0e4658)

# Appendix
## Lessons learned
- Tutorials are often not up to date as the technology changed very frequently.
- Don't forget stopping the cloud services
  
## Resources
### Prometheus
https://logz.io/blog/mongodb-monitoring-prometheus-best-practices/ 

### Grafana:
https://grafana.com/docs/grafana/v9.0/dashboards/export-import/
https://thriftly.io/docs/components/Thriftly-Deployment-Beyond-the-Basics/Metrics-Prometheus/Install-Create-Dashboard-Grafana.html





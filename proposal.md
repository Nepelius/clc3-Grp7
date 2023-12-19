# CLC3 proposal of monitoring with Grafana/Prometheus
## Group Members
* Lukas Nepelius
* Ines Neidhard
* Severin Pichler
## Proposal
The goal is to observe an application with Prometheus and Grafana. Therefore, we first build an application to expose various metrics. The application consists of a DB with a single table in which new entries can be deleted, created and listed via REST API. Then, we will set up Prometheus to collect those metrics and to alert in case of issues (i.e. lot of new entries created in a short time period). Afterwards, we will set up Grafana to visualize our monitored applications. In our demo, we will present Prometheus and Grafana, as well as run a simulation to cause an alert.
## Milestones
1) Create Application for metrics in Python and run it on a Kubernetes Cluster.
   * Application Idea: REST api for creating, deleting and listing entries in a DB (MongoDB or SQLite, ...). The context of the DB could be a note storage for multiple users.
2) Set up Prometheus to collect metrics from Cluster
3) Set up Grafana and connect with Prometheus to visualise metrics 
4) Create a simulaion to test alerts by creating Rules in Prometheus. Alerting via Slack
## Responsibilities
* Lukas: Responsible for setting up Prometheus with our custom application
* Ines: Inegrating Grafana to visualize metrics
* Severin: Building the monitorable application
* All: Deploy application to the cloud

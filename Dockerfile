FROM mcr.microsoft.com/azure-cli:2.55.0

ENV KUBE_LATEST_VERSION="v1.29.0"
ENV HELM_LATEST_VERSION="v3.13.3"
RUN apk add --update ca-certificates \
 && apk add --update -t deps curl \
 && curl -L "https://dl.k8s.io/release/${KUBE_LATEST_VERSION}/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl \
 && chmod +x /usr/local/bin/kubectl \
 && curl -LO "https://get.helm.sh/helm-${HELM_LATEST_VERSION}-linux-amd64.tar.gz" \
 && tar -xvf helm-${HELM_LATEST_VERSION}-linux-amd64.tar.gz \
 && mv linux-amd64/helm /usr/local/bin \
 && rm -f /helm-${HELM_LATEST_VERSION}-linux-amd64.tar.gz \
 && apk del --purge deps \
 && rm /var/cache/apk/*
 
CMD ["bash"]
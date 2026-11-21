FROM registry.access.redhat.com/ubi9-minimal@sha256:08d4c70f1baf6537a0728656cf7942d561e74a35916509d205b6519861266352 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
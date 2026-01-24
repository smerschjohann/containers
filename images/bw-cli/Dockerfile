FROM registry.access.redhat.com/ubi9-minimal@sha256:90bd85dcd061d1ad6dbda70a867c41958c04a86462d05c631f8205e8870f28f8 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
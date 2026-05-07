FROM registry.access.redhat.com/ubi9-minimal@sha256:b9b10f42d7eba7ad4a6d5ef26b7d34fdc892b2ffe59b8d0372ec884008569eb6 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
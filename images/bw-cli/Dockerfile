FROM registry.access.redhat.com/ubi9-minimal@sha256:984df0a2b8d9011d419b0ad260b25f6b74b7ce69ab0595b75522e30f8849f27f as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
FROM registry.access.redhat.com/ubi9-minimal@sha256:dfa0eb04abc59221544e74862432496add1f491f915c9b531880f91affc0e12c as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
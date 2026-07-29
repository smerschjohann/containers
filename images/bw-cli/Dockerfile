FROM registry.access.redhat.com/ubi9-minimal@sha256:17fd831ced9434de0a984d60b3fbe61008308261ba98bbc348d6fbdef05fa7c0 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
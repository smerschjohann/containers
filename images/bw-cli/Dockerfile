FROM registry.access.redhat.com/ubi9-minimal@sha256:daa61d6103e98bccf40d7a69a0d4f8786ec390e2204fd94f7cc49053e9949360 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
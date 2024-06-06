FROM registry.access.redhat.com/ubi9-minimal@sha256:0d6b09f233745d2fcf892cebcf1c18bbfed497f116bc8357e9db4b724d76c5a9 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
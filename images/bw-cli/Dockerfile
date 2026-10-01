FROM registry.access.redhat.com/ubi9-minimal@sha256:1d7c5517a4a1a8e2688620b39ee980e82505ca1ab7ae5541b5463120ae9b3897 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
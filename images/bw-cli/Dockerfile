FROM registry.access.redhat.com/ubi9-minimal@sha256:bafd57451de2daa71ed301b277d49bd120b474ed438367f087eac0b885a668dc as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
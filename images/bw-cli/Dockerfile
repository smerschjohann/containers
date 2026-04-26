FROM registry.access.redhat.com/ubi9-minimal@sha256:7d4e47500f28ac3a2bff06c25eff9127ff21048538ae03ce240d57cf756acd00 as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
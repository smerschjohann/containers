FROM registry.access.redhat.com/ubi9-minimal@sha256:b6ec3ea97ba321c7529b81ae45c407ba8039d52fea3f7b6853734d7f8863344b as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
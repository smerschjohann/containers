FROM registry.access.redhat.com/ubi9-minimal@sha256:ae09ecc3d754bc1726cbda3e2599cc7839e09fe1cc547ce173cf669b645be3cc as app

RUN microdnf -y module enable nodejs:18 && microdnf install -y nodejs
RUN microdnf -y install python3
RUN microdnf -y install make gcc g++
RUN npm install -g @bitwarden/cli
RUN microdnf -y remove make gcc g++ && microdnf clean all
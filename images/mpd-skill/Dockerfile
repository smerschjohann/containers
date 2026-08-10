FROM registry.access.redhat.com/ubi9/ubi-minimal:9.8-1786380870@sha256:7c372902c8d211db2d25c8277ba534a73b92742a334874dced829a63b0f21221 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
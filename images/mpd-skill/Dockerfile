FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1776104705@sha256:fe688da81a696387ca53a4c19231e99289591f990c904ef913c51b6e87d4e4df as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
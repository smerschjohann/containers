FROM registry.access.redhat.com/ubi9/ubi-minimal:9.5-1738643652@sha256:3902bab19972cd054fd08b2a4e08612ae7e68861ee5d9a5cf22d828f27e2f479 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
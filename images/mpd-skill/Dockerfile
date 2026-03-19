FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1773895075@sha256:f225a0f8eb7d258011e1f7c8b025dc7dd155d6ffc66c17cd203dcec88935b455 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
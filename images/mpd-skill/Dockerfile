FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4-1194@sha256:104cf11d890aeb7dd5728b7d7732e175a0e4018f1bb00d2faebcc8f6bf29bd52 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
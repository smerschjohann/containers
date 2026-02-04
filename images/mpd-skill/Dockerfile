FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1770203734@sha256:ecd4751c45e076b4e1e8d37ac0b1b9c7271930c094d1bcc5e6a4d6954c6b2289 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
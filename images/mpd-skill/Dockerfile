FROM registry.access.redhat.com/ubi9/ubi-minimal:9.8-1785906621@sha256:dd334afa72444fa46238fcf9e6bd399245adf746378735348cf84b9dfdca38f1 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
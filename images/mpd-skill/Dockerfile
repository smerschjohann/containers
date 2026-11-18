FROM registry.access.redhat.com/ubi9/ubi-minimal:9.9-1795001629@sha256:d8162789d7913ef8941481687b92ab4bbec311870948f66cf52b9cc7e0c57c06 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
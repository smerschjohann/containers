FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1771346502@sha256:c7d44146f826037f6873d99da479299b889473492d3c1ab8af86f08af04ec8a0 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
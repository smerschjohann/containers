FROM registry.access.redhat.com/ubi9/ubi-minimal:9.3-1612 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
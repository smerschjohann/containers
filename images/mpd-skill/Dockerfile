FROM registry.access.redhat.com/ubi9/ubi-minimal:9.3-1612@sha256:bc552efb4966aaa44b02532be3168ac1ff18e2af299d0fe89502a1d9fabafbc5 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
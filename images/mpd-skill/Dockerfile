FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1777857961@sha256:8d0a8fb39ec907e8ca62cdd24b62a63ca49a30fe465798a360741fde58437a23 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
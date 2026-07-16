FROM registry.access.redhat.com/ubi9/ubi-minimal:9.8-1784092902@sha256:062c52ff973065752b0965787649db2bcf551a6c727a00e95a3eb42cebadbdab as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
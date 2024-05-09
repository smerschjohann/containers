FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4-949.1714662671@sha256:2636170dc55a0931d013014a72ae26c0c2521d4b61a28354b3e2e5369fa335a3 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
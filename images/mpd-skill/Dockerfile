FROM registry.access.redhat.com/ubi9/ubi-minimal:9.8-1790555810@sha256:beeada7dd17903dfb69fd5f6916c054720bf28a52daaa2f7a1910a1394244bd2 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4-1134@sha256:a7d837b00520a32502ada85ae339e33510cdfdbc8d2ddf460cc838e12ec5fa5a as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
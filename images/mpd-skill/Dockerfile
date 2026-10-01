FROM registry.access.redhat.com/ubi9/ubi-minimal:9.8-1790754119@sha256:1d7c5517a4a1a8e2688620b39ee980e82505ca1ab7ae5541b5463120ae9b3897 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.5-1741850109@sha256:bafd57451de2daa71ed301b277d49bd120b474ed438367f087eac0b885a668dc as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
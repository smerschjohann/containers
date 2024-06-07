FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4-949.1717074713@sha256:0d6b09f233745d2fcf892cebcf1c18bbfed497f116bc8357e9db4b724d76c5a9 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
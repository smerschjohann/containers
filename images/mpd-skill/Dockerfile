FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4-949@sha256:b6ec3ea97ba321c7529b81ae45c407ba8039d52fea3f7b6853734d7f8863344b as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
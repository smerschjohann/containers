FROM registry.access.redhat.com/ubi9/ubi-minimal:9.4-949.1716471857@sha256:ef6fb6b3b38ef6c85daebeabebc7ff3151b9dd1500056e6abc9c3295e4b78a51 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
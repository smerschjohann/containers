FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1773939694@sha256:83006d535923fcf1345067873524a3980316f51794f01d8655be55d6e9387183 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
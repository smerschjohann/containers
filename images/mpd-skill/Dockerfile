FROM registry.access.redhat.com/ubi9/ubi-minimal:9.8-1788939036@sha256:d235f607e1d6d833f031db107dc42206e4dd4d5aa9142c43d3771fb7f9bea76a as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
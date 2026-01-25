FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1768783948@sha256:90bd85dcd061d1ad6dbda70a867c41958c04a86462d05c631f8205e8870f28f8 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
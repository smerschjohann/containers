FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6-1754000177@sha256:0d7cfb0704f6d389942150a01a20cb182dc8ca872004ebf19010e2b622818926 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.8-1788166357@sha256:7fbeae18dc9476399f565e68255f602a3374ea8614ba3d14843565131a13ff93 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
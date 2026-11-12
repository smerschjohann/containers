FROM registry.access.redhat.com/ubi9/ubi-minimal:9.9-1793829856@sha256:ecb40c7bdfa5b0bb71e978c98c7cf56ce38edf1f8fb3561078acbc4b13698c07 as skill

RUN microdnf install -y python3 pip

COPY . /src

WORKDIR /src
RUN pip install -r requirements.txt

CMD python3 lambda_function.py
FROM docker.io/library/golang:alpine@sha256:98e6cffc31ccc44c7c15d83df1d69891efee8115a5bb7ede2bf30a38af3e3c92 AS builder
WORKDIR /app

RUN apk --update add --no-cache ca-certificates openssl git tzdata && update-ca-certificates

COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN  GO111MODULE="on" CGO_ENABLED=0 GOOS=linux go build -o aiskill .

FROM scratch AS app
LABEL maintainer="Simon Merschjohann"
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

WORKDIR /app
COPY --from=builder /app/aiskill .
EXPOSE 8080
CMD ["/app/aiskill"]

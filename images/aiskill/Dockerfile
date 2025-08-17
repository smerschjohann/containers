FROM docker.io/library/golang:alpine@sha256:f18a072054848d87a8077455f0ac8a25886f2397f88bfdd222d6fafbb5bba440 AS builder
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

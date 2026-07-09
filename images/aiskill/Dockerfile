FROM docker.io/library/golang:alpine@sha256:0178a641fbb4858c5f1b48e34bdaabe0350a330a1b1149aabd498d0699ff5fb2 AS builder
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

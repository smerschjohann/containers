FROM docker.io/library/golang:alpine@sha256:7772cb5322baa875edd74705556d08f0eeca7b9c4b5367754ce3f2f00041ccee AS builder
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

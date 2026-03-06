FROM docker.io/library/golang:alpine@sha256:2389ebfa5b7f43eeafbd6be0c3700cc46690ef842ad962f6c5bd6be49ed82039 AS builder
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

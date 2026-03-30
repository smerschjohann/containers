FROM rockylinux/rockylinux:10-minimal@sha256:cfa2812ec7151c2be393cfe46e50cf59426373d12f03f4ffbdd56becb8195a65 as squid
RUN microdnf -y install squid && \
    microdnf clean all

EXPOSE 3128

USER squid

# Startbefehl: -N = nicht forken (Vordergrundbetrieb für Docker), -Y = schneller Start (DNS-Check verzögern)
CMD [ "squid", "-NYd", "1" ]
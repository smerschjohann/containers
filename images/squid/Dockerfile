FROM rockylinux/rockylinux:10-minimal@sha256:bc5c1e7a2ec7f4bcef1e51c7f0ebb2d43f05409e0108cdd34f693921d0604360 as squid
RUN microdnf -y install squid && \
    microdnf clean all

EXPOSE 3128

USER squid

# Startbefehl: -N = nicht forken (Vordergrundbetrieb für Docker), -Y = schneller Start (DNS-Check verzögern)
CMD [ "squid", "-NYd", "1" ]
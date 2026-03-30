FROM rockylinux/rockylinux:10-minimal as squid
RUN microdnf -y install squid && \
    microdnf clean all

EXPOSE 3128

USER squid

# Startbefehl: -N = nicht forken (Vordergrundbetrieb für Docker), -Y = schneller Start (DNS-Check verzögern)
CMD [ "squid", "-NYd", "1" ]
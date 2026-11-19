FROM rockylinux/rockylinux:10-minimal@sha256:f819149e93579b96a7e2fb7286dae4756173de68aafcc78e7e659650c6867b7b as squid
RUN microdnf -y install squid && \
    microdnf clean all

EXPOSE 3128

USER squid

# Startbefehl: -N = nicht forken (Vordergrundbetrieb für Docker), -Y = schneller Start (DNS-Check verzögern)
CMD [ "squid", "-NYd", "1" ]
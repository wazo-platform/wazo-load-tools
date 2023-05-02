FROM internetsystemsconsortium/bind9:9.18

RUN apt update \
  && apt install -y \
  bind9-doc \
  dnsutils \
  geoip-bin \
  mariadb-server \
  net-tools

COPY bind.sh /usr/local/bin/bind.sh

# Expose Ports
EXPOSE 53/tcp
EXPOSE 53/udp
EXPOSE 953/tcp

# Start the Name Service
CMD ["/usr/local/bin/bind.sh"]

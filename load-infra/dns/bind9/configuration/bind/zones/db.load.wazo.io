$TTL    1d ; default expiration time (in seconds) of all RRs without their own TTL value
@       IN      SOA     ns1.load.wazo.io. root.load.wazo.io. (
                  3      ; Serial
                  1d     ; Refresh
                  1h     ; Retry
                  1w     ; Expire
                  1h )   ; Negative Cache TTL

; name servers - NS records
@           IN      NS      ns1.load.wazo.io.

; name servers - A records
ns1.load.wazo.io.                    IN      A      172.16.43.79
registry.load.wazo.io.               IN      A      172.16.43.79
trafgen1.load.wazo.io.               IN      A      172.16.43.25
trafgen2.load.wazo.io.               IN      A      172.16.43.236
trafgen3.load.wazo.io.               IN      A      172.16.43.218
grafana.load.wazo.io.                IN      A      172.16.43.33
wazo-500.load.wazo.io.               IN      A      172.16.43.10
wazo-1000.load.wazo.io.        	     IN      A      172.16.43.95
wazo-1000-extra.load.wazo.io.        IN      A      172.16.43.42
wazo-5000.load.wazo.io.              IN      A      172.24.0.3


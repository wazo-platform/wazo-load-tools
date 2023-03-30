.PHONY: tar-trafgen tar-dns tar-registry tar-prometheus


BASE = ${PWD}
INFRA = $(BASE)/load-infra
LOAD = $(BASE)/load-generator

tar-trafgen:
	cd $(INFRA)/trafgen-node && \
	tar -cvf  $(INFRA)/trafgen.tar usr && \
	tar -rvf $(INFRA)/trafgen.tar etc && \
	tar -rvf $(INFRA)/trafgen.tar opt && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/trafgen.tar etc && \
	tar -rvf $(INFRA)/trafgen.tar usr && \
	cd $(LOAD)/ && \
	tar -rvf $(INFRA)/trafgen.tar etc


tar-dns:
	cd $(INFRA)/dns && \
	tar -cvf  $(INFRA)/dns.tar usr && \
	tar -rvf $(INFRA)/dns.tar etc && \
	tar -rvf $(INFRA)/dns.tar opt && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/dns.tar etc && \
	tar -rvf $(INFRA)/dns.tar usr 


tar-prometheus:
	cd $(INFRA)/prometheus && \
	tar -cvf  $(INFRA)/prometheus.tar usr && \
	tar -rvf $(INFRA)/prometheus.tar etc && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/prometheus.tar etc && \
	tar -rvf $(INFRA)/prometheus.tar usr 


tar-registry:
	cd $(INFRA)/registry && \
	tar -cvf  $(INFRA)/registry.tar usr && \
	tar -rvf $(INFRA)/registry.tar etc && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/registry.tar etc && \
	tar -rvf $(INFRA)/registry.tar usr 

tar-controller:
	cd $(INFRA)/controller && \
	tar -cvf  $(INFRA)/controller.tar usr && \
	tar -rvf $(INFRA)/controller.tar etc && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/controller.tar etc && \
	tar -rvf $(INFRA)/controller.tar usr 

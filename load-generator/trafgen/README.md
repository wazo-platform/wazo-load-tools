# Trafgen 

## Containers
2 containers are stacked to build trafgen.
- The first one is the sipp the underlying tool to generate traffic over the wazo stack
- The second one is trafgen based on xivo-load-tester
  

 # How it works
The main script trafgen.sh is used to run the different senarios. 
This script is setup by the trafgen.env variable file which is 
sourced by the docker exec command. Here an example of such command
in the `load-test` target that can be found in the [load-generator/Makefile](../Makefile)
There is also a `SCENARIO` env variable that is used to specify the scenario to run.
As scenarios are less static than configuration it is more convenient to use an inline
variable for automation purpose.

```
ENVS ?= trafgen/trafgen.env
load_test: $(ENVS)
	docker exec -it --env-file $(ENVS) trafgen bash -c "/trafgen/load-tests.sh"
```


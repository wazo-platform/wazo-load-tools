cat ~/bin/reload-bind.sh 
#!/bin/bash -x
docker exec -d ddns-master bash -c "rndc reload"

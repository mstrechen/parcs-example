![PARCS logo](/logo.png)

This is an example of problem solution based on language agnostic PARCS implementation (see [lionell/parcs](lionell_parcs))

#### How to run

First, you need to run PARCS on your cluster. For this step, please use lionell's [manual](setup_manual).

Next, just use your `leader` machine (with `$ gcloud compute ssh leader`) and run something like:
```.bash
$ LEADER=tcp://<leader address in cluster>:4321
$ IMAGE=mstrechen/largest-common-subseqence-runner-py:latest
$ WORKERS=<number of workers>
$ sudo docker service create \
        --name runner \
        --network parcs \
        --restart-condition none \
        --env LEADER_URL=$LEADER \
        --env WORKERS=$WORKERS \
        --env N=100000 \
        --env M=300 \
        --env SEED=10 \
        $IMAGE
```

Use swarmpit ui to get worker/leader logs :) 


#### Running your own image

For this you have to use your own DockerHub repository. 
Something like:
```
docker build -t <your_repo>/largest-common-subseqence-runner:latest .
docker push <your_repo>/largest-common-subseqence-runner:latest
```
Now you are able to run your own **runner** with the same command as before - just set your own `IMAGE` variable.

For worker replacement you also have to build & push an image, but at the same time don't forget to 
change image name in the code of `runner` (see `task = self.engine.run('mstrechen/largest-common-subseqence-worker-go')` line in main.py)


[lionell_parcs]: https://github.com/lionell/parcs
[setup_manual]: https://github.com/lionell/parcs#swarm-cluster-on-gcp
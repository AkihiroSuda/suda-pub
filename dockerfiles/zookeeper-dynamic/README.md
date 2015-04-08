ZooKeeper with dynamic configuration
===
Requirements
---
 * ["zookeeper" directory](https://github.com/apache/zookeeper) is located on this directory
 * Open vSwitch is installed
 * 192.168.42.254/24 is assigned to Open vSwitch bridge named "ovsbr0"
 * [pipework](https://github.com/jpetazzo/pipework) is installed

If those requirements are not satisfied:

```
$ git clone https://github.com/apache/zookeeper
$ sudo apt-get install -y openvswitch-switch
$ sudo ip addr add 192.168.42.254/24 dev ovsbr0 # you should add this line to your /etc/rc.local
$ sudo apt-get install -y arping # required by pipework
$ sudo wget --no-check-certificate --quiet https://raw.github.com/jpetazzo/pipework/master/pipework -O /usr/local/bin/pipework
$ sudo chmod +x /usr/local/bin/pipework
```

Build
---
```
$ docker build -t akihirosuda/zookeeper-dynamic .
```

Usage
---
The initial ensemble is composed of [ZKID=1, 2, 3]. 4 and 5 are just observers. (See init.py)
```
$ for f in $(seq 1 5); do \
    docker run -d -e ZKID=${f} -h zk${f} --name zk${f} akihirosuda/zookeeper-dynamic; \
    sudo pipework ovsbr0 zk${f} 192.168.42.${f}/24; \
  done
```

Initial View from ZKID=1 (as a participant):
```
$ ( cd zookeeper; ant )
$ ./zookeeper/bin/zkCli.sh -server 192.168.42.1 config
server.1=192.168.42.1:2888:3888:participant;0.0.0.0:2181
server.2=192.168.42.2:2888:3888:participant;0.0.0.0:2181
server.3=192.168.42.3:2888:3888:participant;0.0.0.0:2181
version=100000000
```

Initial View from ZKID=4 (as an observer):
```
$ ./zookeeper/bin/zkCli.sh -server 192.168.42.4 config
server.1=192.168.42.1:2888:3888:participant;0.0.0.0:2181
server.2=192.168.42.2:2888:3888:participant;0.0.0.0:2181
server.3=192.168.42.3:2888:3888:participant;0.0.0.0:2181
version=100000000
```

Reconfig [1,2,3]->[1,2,3,4] (ZKID 4: observer->participant):
```
$ ./zookeeper/bin/zkCli.sh -server 192.168.42.1 reconfig -add server.4=192.168.42.4:288:3888\;2181
itted new configuration:
server.1=192.168.42.1:2888:3888:participant;0.0.0.0:2181
server.2=192.168.42.2:2888:3888:participant;0.0.0.0:2181
server.3=192.168.42.3:2888:3888:participant;0.0.0.0:2181
server.4=192.168.42.4:288:3888:participant;0.0.0.0:2181
version=10000000a
```

Reconfig [1,2,3,4]->[5] (ZKID 5: observer->participant, others: participant->non-voting follower):
```
$ ./zookeeper/bin/zkCli.sh -server 192.168.42.1 reconfig -members server.5=192.168.42.5:288:3888\;2181
Committed new configuration:
server.5=192.168.42.5:288:3888:participant;0.0.0.0:2181
version=10000000e
```


Tips
---
Manual start mode:
```
 $ for f in $(seq 1 5); do \
     docker run -i -t -d -e ZKID=${f} -h zk${f} --name zk${f} akihirosuda/zookeeper-dynamic /bin/bash; \
     sudo pipework ovsbr0 zk${f} 192.168.42.${f}/24; \
   done
$ docker attach zk1
zk1% /init.py
```

Set Heap size: Add `-e JVMFLAGS='-Xms128m -Xmx128m'`

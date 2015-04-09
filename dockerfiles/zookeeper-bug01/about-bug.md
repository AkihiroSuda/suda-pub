# A specific order of reconfig and crash/restart with a badly rolled-back conf leads to infinite exception loop
## Abstract
This sequence leads 1 and 2 to infinite exception loop

 * Start 1 and 2 with the initial ensemble [1]
 * Reconfig [1]->[1,2]
 * Reconfig [1,2]->[2]
 * Stop 2 (SIGKILL)
 * Start 2 with the initial ensemble [1] (roll-back conf directory to the initial version before starting)
 * 1 and 2 begin infinite exception loop; 1 will not respond to telnet/ZkCli (2 still responds)

NOTE: the bug cannot be always reproduced due to non-determinism. 
 
## Cause
ZooKeeper cannot handle unexpected configuration roll-backs, which can be caused by bad (user-written) server init scripts.

org.apache.zookeeper.server.quorum.Follower.followLeader should handle such an exception?


## Version
ZooKeeper@f5fb50ed2591ba9a24685a227bb5374759516828 (Apr 7, 2015)


## Config
### Server 1
    tickTime=2000
    initLimit=10
    syncLimit=5
    dataDir=/zk_data
    standaloneEnabled=false
    server.1=192.168.42.1:2888:3888:participant;2181

### Server 2
    tickTime=2000
    initLimit=10
    syncLimit=5
    dataDir=/zk_data
    standaloneEnabled=false
    server.1=192.168.42.1:2888:3888:participant;2181
    server.2=192.168.42.2:2888:3888:observer;2181
    

## Log
NOTE: These logs were captured with ZooKeeper@ca480231e1bdcbe6beda9142766fc3caa2031cd8 (Feb 11 2015)
### Server 1
    2015-02-18 01:36:30,185 [myid:1] - WARN  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:Follower@93] - Exception when following the leader
    java.io.IOException: Leaders epoch, 1 is less than accepted epoch, 2
            at org.apache.zookeeper.server.quorum.Learner.registerWithLeader(Learner.java:297)
            at org.apache.zookeeper.server.quorum.Follower.followLeader(Follower.java:75)
            at org.apache.zookeeper.server.quorum.QuorumPeer.run(QuorumPeer.java:963)
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:MBeanRegistry@119] - Unregister MBean [org.apache.ZooKeeperService:name0=ReplicatedServer_id1,name1=replica.1,name2=Follower]
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:Follower@198] - shutdown called
    java.lang.Exception: shutdown Follower
            at org.apache.zookeeper.server.quorum.Follower.shutdown(Follower.java:198)
            at org.apache.zookeeper.server.quorum.QuorumPeer.run(QuorumPeer.java:967)
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:LearnerZooKeeperServer@161] - Shutting down
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:ZooKeeperServer@440] - shutting down
    2015-02-18 01:36:30,185 [myid:1] - WARN  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:QuorumPeer@1010] - PeerState set to LOOKING
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:QuorumPeer@885] - LOOKING
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:FileSnap@83] - Reading snapshot /zk_data/version-2/snapshot.100000006
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:FastLeaderElection@889] - New election. My id =  1, proposed zxid=0x200000001
    2015-02-18 01:36:30,185 [myid:1] - INFO  [WorkerReceiver[myid=1]:FastLeaderElection@683] - Notification: 2 (message format version), 2 (n.leader), 0x0 (n.zxid), 0x1 (n.round), LEADING (n.state), 2 (n.sid), 0x1 (n.peerEPoch), LOOKING (my state)100000006 (n.config version)
    2015-02-18 01:36:30,185 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:MBeanRegistry@119] - Unregister MBean [org.apache.ZooKeeperService:name0=ReplicatedServer_id1,name1=replica.1,name2=LeaderElection]
    2015-02-18 01:36:30,186 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:QuorumPeer@961] - FOLLOWING
    2015-02-18 01:36:30,186 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:ZooKeeperServer@778] - minSessionTimeout set to 4000
    2015-02-18 01:36:30,186 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:ZooKeeperServer@787] - maxSessionTimeout set to 40000
    2015-02-18 01:36:30,186 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:ZooKeeperServer@153] - Created server with tickTime 2000 minSessionTimeout 4000 maxSessionTimeout 40000 datadir /zk_data/version-2 snapdir /zk_data/version-2
    2015-02-18 01:36:30,186 [myid:1] - INFO  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:Follower@66] - FOLLOWING - LEADER ELECTION TOOK - 0
    2015-02-18 01:36:30,186 [myid:1] - WARN  [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:Follower@93] - Exception when following the leader
    java.io.IOException: Leaders epoch, 1 is less than accepted epoch, 2
            at org.apache.zookeeper.server.quorum.Learner.registerWithLeader(Learner.java:297)
            at org.apache.zookeeper.server.quorum.Follower.followLeader(Follower.java:75)
            at org.apache.zookeeper.server.quorum.QuorumPeer.run(QuorumPeer.java:963)
    

### Server 2
    2015-02-18 01:36:37,420 [myid:2] - WARN  [LearnerHandler-/192.168.42.1:45144:LearnerHandler@595] - ******* GOODBYE /192.168.42.1:45144 ********
    2015-02-18 01:36:37,421 [myid:2] - INFO  [LearnerHandler-/192.168.42.1:45145:LearnerHandler@364] - Follower sid: 1 not in the current config 100000006
    2015-02-18 01:36:37,421 [myid:2] - ERROR [LearnerHandler-/192.168.42.1:45145:LearnerHandler@580] - Unexpected exception causing shutdown while sock still open
    java.io.EOFException
            at java.io.DataInputStream.readInt(DataInputStream.java:392)
            at org.apache.jute.BinaryInputArchive.readInt(BinaryInputArchive.java:63)
            at org.apache.zookeeper.server.quorum.QuorumPacket.deserialize(QuorumPacket.java:83)
            at org.apache.jute.BinaryInputArchive.readRecord(BinaryInputArchive.java:103)
            at org.apache.zookeeper.server.quorum.LearnerHandler.run(LearnerHandler.java:392)
    2015-02-18 01:36:37,421 [myid:2] - WARN  [LearnerHandler-/192.168.42.1:45145:LearnerHandler@595] - ******* GOODBYE /192.168.42.1:45145 ********
    2015-02-18 01:36:37,422 [myid:2] - INFO  [LearnerHandler-/192.168.42.1:45146:LearnerHandler@364] - Follower sid: 1 not in the current config 100000006
    2015-02-18 01:36:37,422 [myid:2] - ERROR [LearnerHandler-/192.168.42.1:45146:LearnerHandler@580] - Unexpected exception causing shutdown while sock still open
    java.io.EOFException
            at java.io.DataInputStream.readInt(DataInputStream.java:392)
            at org.apache.jute.BinaryInputArchive.readInt(BinaryInputArchive.java:63)
            at org.apache.zookeeper.server.quorum.QuorumPacket.deserialize(QuorumPacket.java:83)
            at org.apache.jute.BinaryInputArchive.readRecord(BinaryInputArchive.java:103)
            at org.apache.zookeeper.server.quorum.LearnerHandler.run(LearnerHandler.java:392)


## Addendum
These sequences seem to be OK (not sure right now; maybe related to non-determinism):

 * OK
  * Start [1,2] with the initial ensemble [1,2]
  * Reconfig [1,2]->[2]
  * Stop [2] (SIGKILL)
  * Start [2] with the initial ensemble [1,2] (revert conf to the initial version before starting)

 * OK
  * Start [1,2] with the initial ensemble [1]
  * Reconfig [1]->[1,2]
  * Reconfig [1,2]->[2]
  * Stop [2] (SIGKILL)
  * Start [2] with the initial ensemble [2] (Do NOT revert conf to the initial version before starting)


These sequences are NG:

 * NG
  * Start [1,2] with the initial ensemble [1]
  * Reconfig [1]->[1,2]
  * Reconfig [1,2]->[2]
  * Stop [2] (SIGKILL)
  * Start [2] with the initial ensemble [2] (modify conf manually before starting)

 * NG
  * Start [1,2,3,4,5] with the initial ensemble [1,2,3]
  * Reconfig [1,2,3]->[1,2,3,4]
  * Reconfig [1,2,3,4]->[5]
  * Stop [5] (SIGKILL)
  * Start [5] with the initial ensemble [1,2,3] (revert conf to the initial version before starting)

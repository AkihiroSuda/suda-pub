ZooKeeper bug reproduction: infinite exception loop occurs when dataDir is lost
===
This container reproduces the bug.

Reproduction
---

    $ docker run -i -t --rm akihirosuda/zookeeper-bug01
    Reproducing the bug: infinite exception loop occurs when dataDir is lost
    * Resetting
    * Starting [1,2] with the initial ensemble [1]
    * Sleeping for 3 seconds
    * Invoking Reconfig [1]->[2]
    * Sleeping for 3 seconds
    * Killing server.2 (pid=10542)
    * Sleeping for 3 seconds
    * Resetting /zk02_data
    * Starting server.2
    * Sleeping for 30 seconds
    /zk01_log: 81665114 bytes
    The log dir is extremely large. Perhaps the bug was REPRODUCED!
    /zk02_log: 23949367 bytes
    The log dir is extremely large. Perhaps the bug was REPRODUCED!
    * Exiting

## About the bug
This sequence leads server.1 and server.2 to infinite exception loop.

 * Start server.1 and server.2 with the initial ensemble server.1=participant, server.2=observer.
   In this time, acceptedEpoch[i] == currentEpoch[i] == 1 for i = 1, 2.
 * Invoke reconfig so that acceptedEpoch[i] and currentEpoch[i] grows up to 2.
 * Kill server.2
 * Remove dataDir of server.2 excluding the myid file.
   (In real production environments, both of confDir and dataDir can be lost due to reprovisioning)
 * Start server.2
 * server.1 and server.2 enters infinite exception loop.
   The log (threshold is set to INFO in log4j.properties) size can reach > 100MB in 30 seconds.

AFAIK, the bug can be reproduced with ZooKeeper@f5fb50ed2591ba9a24685a227bb5374759516828 (Apr 7, 2015).

## Log
### server.1

    2015-04-13 03:48:17,624 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):QuorumPeer@1022] - FOLLOWING
    2015-04-13 03:48:17,624 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):ZooKeeperServer@825] - minSessionTimeout set to 4000
    2015-04-13 03:48:17,624 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):ZooKeeperServer@834] - maxSessionTimeout set to 40000
    2015-04-13 03:48:17,624 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):ZooKeeperServer@156] - Created server with tickTime 2000 minSession
    Timeout 4000 maxSessionTimeout 40000 datadir /zk01_data/version-2 snapdir /zk01_data/version-2
    2015-04-13 03:48:17,624 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):Follower@66] - FOLLOWING - LEADER ELECTION TOOK - 0
    2015-04-13 03:48:17,625 [myid:1] - WARN  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):Follower@93] - Exception when following the leader
    java.io.IOException: Leaders epoch, 1 is less than accepted epoch, 2
            at org.apache.zookeeper.server.quorum.Learner.registerWithLeader(Learner.java:331)
            at org.apache.zookeeper.server.quorum.Follower.followLeader(Follower.java:75)
            at org.apache.zookeeper.server.quorum.QuorumPeer.run(QuorumPeer.java:1024)
    2015-04-13 03:48:17,626 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):MBeanRegistry@119] - Unregister MBean [org.apache.ZooKeeperService:
    name0=ReplicatedServer_id1,name1=replica.1,name2=Follower]
    2015-04-13 03:48:17,626 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):Follower@198] - shutdown called
    java.lang.Exception: shutdown Follower
            at org.apache.zookeeper.server.quorum.Follower.shutdown(Follower.java:198)
            at org.apache.zookeeper.server.quorum.QuorumPeer.run(QuorumPeer.java:1028)
    2015-04-13 03:48:17,626 [myid:1] - DEBUG [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):LearnerZooKeeperServer@162] - ZooKeeper server is not running, so n
    ot proceeding to shutdown!
    2015-04-13 03:48:17,626 [myid:1] - WARN  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):QuorumPeer@1071] - PeerState set to LOOKING
    2015-04-13 03:48:17,626 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):QuorumPeer@946] - LOOKING
    2015-04-13 03:48:17,626 [myid:1] - DEBUG [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):QuorumPeer@875] - Initializing leader election protocol...
    2015-04-13 03:48:17,626 [myid:1] - DEBUG [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):FastLeaderElection@790] - Updating proposal: -9223372036854775808 (
    newleader), 0x100000002 (newzxid), -9223372036854775808 (oldleader), 0x100000002 (oldzxid)
    2015-04-13 03:48:17,626 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):FastLeaderElection@889] - New election. My id =  1, proposed zxid=0
    x100000002
    2015-04-13 03:48:17,626 [myid:1] - DEBUG [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):FastLeaderElection@673] - Sending Notification: -922337203685477580
    8 (n.leader), 0x100000002 (n.zxid), 0x2 (n.round), 2 (recipient), 1 (myid), 0x2 (n.peerEpoch)
    2015-04-13 03:48:17,626 [myid:1] - DEBUG [WorkerSender[myid=1]:QuorumCnxManager@400] - There is a connection already for server 2
    2015-04-13 03:48:17,627 [myid:1] - DEBUG [WorkerReceiver[myid=1]:FastLeaderElection$Messenger$WorkerReceiver@336] - Receive new notification message. My id = 1
    2015-04-13 03:48:17,627 [myid:1] - INFO  [WorkerReceiver[myid=1]:FastLeaderElection@683] - Notification: 2 (message format version), 2 (n.leader), 0x0 (n.zxid), 0x1 (n.round)
    , LEADING (n.state), 2 (n.sid), 0x1 (n.peerEPoch), LOOKING (my state)100000002 (n.config version)
    2015-04-13 03:48:17,627 [myid:1] - DEBUG [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):FastLeaderElection@812] - I'm a participant: 1
    2015-04-13 03:48:17,627 [myid:1] - DEBUG [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):FastLeaderElection@637] - About to leave FLE instance: leader=2, zx
    id=0x0, my id=1, my state=FOLLOWING
    2015-04-13 03:48:17,627 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):MBeanRegistry@119] - Unregister MBean [org.apache.ZooKeeperService:
    name0=ReplicatedServer_id1,name1=replica.1,name2=LeaderElection]
    2015-04-13 03:48:17,627 [myid:1] - INFO  [QuorumPeer[myid=1](plain=/0:0:0:0:0:0:0:0:2181)(secure=disabled):QuorumPeer@1022] - FOLLOWING
    ..
    

### server.2

    2015-04-13 03:48:17,672 [myid:2] - ERROR [LearnerHandler-/127.0.0.1:36337:LearnerHandler@580] - Unexpected exception causing shutdown while sock still open
    java.io.EOFException
            at java.io.DataInputStream.readInt(DataInputStream.java:392)
            at org.apache.jute.BinaryInputArchive.readInt(BinaryInputArchive.java:63)
            at org.apache.zookeeper.server.quorum.QuorumPacket.deserialize(QuorumPacket.java:83)
            at org.apache.jute.BinaryInputArchive.readRecord(BinaryInputArchive.java:99)
            at org.apache.zookeeper.server.quorum.LearnerHandler.run(LearnerHandler.java:392)
    2015-04-13 03:48:17,672 [myid:2] - WARN  [LearnerHandler-/127.0.0.1:36337:LearnerHandler@595] - ******* GOODBYE /127.0.0.1:36337 ********
    2015-04-13 03:48:17,674 [myid:2] - DEBUG [WorkerSender[myid=2]:QuorumCnxManager@400] - There is a connection already for server 1
    2015-04-13 03:48:17,676 [myid:2] - INFO  [LearnerHandler-/127.0.0.1:36338:LearnerHandler@364] - Follower sid: 1 not in the current config 100000002
    2015-04-13 03:48:17,676 [myid:2] - ERROR [LearnerHandler-/127.0.0.1:36338:LearnerHandler@580] - Unexpected exception causing shutdown while sock still open
    java.io.EOFException
            at java.io.DataInputStream.readInt(DataInputStream.java:392)
            at org.apache.jute.BinaryInputArchive.readInt(BinaryInputArchive.java:63)
            at org.apache.zookeeper.server.quorum.QuorumPacket.deserialize(QuorumPacket.java:83)
            at org.apache.jute.BinaryInputArchive.readRecord(BinaryInputArchive.java:99)
            at org.apache.zookeeper.server.quorum.LearnerHandler.run(LearnerHandler.java:392)
    2015-04-13 03:48:17,677 [myid:2] - WARN  [LearnerHandler-/127.0.0.1:36338:LearnerHandler@595] - ******* GOODBYE /127.0.0.1:36338 ********
    ..
    

## Workaround

PATCH: [0001-Learner-shutdown-when-the-leader-s-epoch-is-less-tha.patch](0001-Learner-shutdown-when-the-leader-s-epoch-is-less-tha.patch)

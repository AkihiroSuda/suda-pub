ZooKeeper bug reproduction
===
Please refer to about-bug.md.
This container reproduces the bug.

Usage
---
    $ docker run -i -t --rm akihirosuda/zookeeper-bug01
    Reproducing the bug: "A specific order of reconfig and crash/restart with a badly rolled-back conf leads to infinite exception loop"
    Resetting..
    Starting [1,2] with the initial ensemble [1]
    Invoking Reconfig [1]->[1,2]
    Invoking Reconfig [1,2]->[2]
    Killing server.2 (pid=63)
    Resetting server.2 to the initial ensemble [2]
    Starting server.2
    Sleeping for 30 seconds
    /zk01_log: 81666585 bytes
    The log dir is extremely large. Perhaps the bug was REPRODUCED!
    /zk02_log: 23952215 bytes
    The log dir is extremely large. Perhaps the bug was REPRODUCED!
    If the bug was not reproduced, please try to replace /zk and run /init.py again
    AFAIK the bug can be reproduced with f5fb50ed2591ba9a24685a227bb5374759516828 (Apr 7, 2015).
    Dropping to shell..
    root@33d419bcc866:/# logout
    Exiting..

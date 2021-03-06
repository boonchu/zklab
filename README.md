###### [ZooKeeper](http://www.slideshare.net/jimmy_lai/distributed-system-coordination-by-zookeeper-and-introduction-to-kazoo-python-library)
* ZooKeeper has been using in many application which need service discovery lookup. 

* How to build it on Cent OS 7.x
```
  *  git clone https://github.com/skottler/zookeeper-rpms
  *  cd zookeeper-rpms
  *  rpmdev-setuptree
  *  spectool -g zookeeper.spec
  *  rpmbuild -bs --nodeps --define "_sourcedir ." --define "_srcrpmdir ." zookeeper.spec
  *  sudo mock <the srpm from step 5>
```
* sample result
```
$ tree /var/lib/mock/epel-7-x86_64/result/
/var/lib/mock/epel-7-x86_64/result/
├── build.log
├── libzookeeper-3.4.6-2.x86_64.rpm
├── libzookeeper-devel-3.4.6-2.x86_64.rpm
├── root.log
├── state.log
├── zookeeper-3.4.6-2.src.rpm
├── zookeeper-3.4.6-2.x86_64.rpm
└── zookeeper-debuginfo-3.4.6-2.x86_64.rpm

0 directories, 8 file
```
* test install and promote it to artifactory
```
bigchoo@server1 1060 \> sudo yum localinstall /var/lib/mock/epel-7-x86_64/result/libzookeeper-3.4.6-2.x86_64.rpm  /var/lib/mock/epel-7-x86_64/result/zookeeper-3.4.6-2.x86_64.rpm
```
* update service unit files 
```
$ sudo systemctl enable zookeeper
$ sudo systemctl start zookeeper
```

###### Working with CLI
* follow these instructions to download CLI tool
  * [git source](https://github.com/davidledwards/zookeeper/tree/master/zookeeper-cli)
  * [binary download latest 1.3](https://oss.sonatype.org/content/groups/public/com/loopfor/zookeeper/zookeeper-cli/1.3/)
```
bigchoo@vmk2 904 $ ./zk --version
zk 1.3
bigchoo@server1 1121 \> ./zk server1:2181
connecting to {server1:2181} @ / ...
zk> ls /foo/bar
/foo/bar: no such node
zk> mk -r /foo/bar
zk> ls /foo/bar
zk> set -v 0 /foo/bar "hello world"
zk> setacl -v 0 /foo/bar world:anyone=rw
zk> get /foo/bar
00000000  68 65 6c 6c 6f 20 77 6f 72 6c 64                 |hello world     |
zk> stat -c /foo/bar
3 6 3 2015-02-27T09:24:55.875-0800 2015-02-27T09:26:36.104-0800 1 0 1 0 11 0
zk> getacl /foo/bar
3,s{'world,'anyone}
zk> rm -v 1 /foo/bar
```
###### Zookeeper Cluster setup
* pull yum rpm package from artifactory and install to two provided extra nodes
* test connection if service running?
```
root@server1 1016 \> for i in server1 vmk1 vmk2 ; do   echo "ping host $i"; echo "ruok" | nc $i 2181; echo ; done
ping host server1
imok
ping host vmk1
imok
ping host vmk2
imok
```
* populate configuration for each worker
```
root@vmk1 263 $ cat /etc/zookeeper/zoo.cfg
# The number of milliseconds of each tick
tickTime=2000
# The number of ticks that the initial
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
dataDir=/var/lib/zookeeper/data
# the port at which the clients will connect
clientPort=2181

# Enable regular purging of old data and transaction logs every 24 hours
autopurge.purgeInterval=24
autopurge.snapRetainCount=5

server.1=server1:2888:3888
server.2=vmk1:2888:3888
server.3=vmk2:2888:3888
```
* add myid file for each worker and restart zk
```
root@server1 264 $ echo "1" > /var/lib/zookeeper/data/myid
root@vmk1 264 $ echo "2" > /var/lib/zookeeper/data/myid
root@vmk2 264 $ echo "3" > /var/lib/zookeeper/data/myid
```
* verify all nodes and find who is the leader
* shutdown one node (server1) while query service name.
```
bigchoo@server1 1173 \> ./zk server1:2181 vmk1:2181 vmk2:2181
connecting to {server1:2181,vmk1:2181,vmk2:2181} @ / ...
zk> ls /foo/bar
hello world
>>> I shutdown server1 service.

root@server1 1000 \> systemctl stop zookeeper
[12:04 Fri Feb 27] /home/bigchoo
root@server1 1001 \> echo "ruok" | nc server1 2181
Ncat: Connection refused.

zk> ls /foo/bar
hello world
```
* when I took service down from 2 nodes out of 3. Quorum changes and falls below 50%.
```
root@server1 1003 \> ./zk server1:2181 vmk1:2181 vmk2:2181
connecting to {server1:2181,vmk1:2181,vmk2:2181} @ / ...
zk> ls /foo/bar
/foo/bar: no such node
```
###### Start with Kazoo
```
$ sudo yum install -y python-kazoo
bigchoo@server1 ~/lab/zklab (master)*$ ./kz_con.py
connected
bigchoo@server1 ~/lab/zklab (master)*$ /tmp/zookeeper-cli-1.3/bin/zk server1:2181 vmk1:2181 vmk2:2181
connecting to {server1:2181,vmk1:2181,vmk2:2181} @ / ...
zk> ls /path
zk> get /path
00000000  64 61 74 61 5f 73 74 72 69 6e 67                 |data_string     |
```
###### Zookeeper Chef
```
$ knife cookbook site download zookeeper
Downloading zookeeper from the cookbooks site at version 2.5.1 to /home/bigchoo/Cheflabs/zookeeper-2.5.1.tar.gz
Cookbook saved: /home/bigchoo/Cheflabs/zookeeper-2.5.1.tar.gz
```
* Reference
  - [Used cluster instructions from Storm setup](http://www.michael-noll.com/tutorials/running-multi-node-storm-cluster/)
  - [Multi Server Zookeeper setup](http://zookeeper.apache.org/doc/r3.3.3/zookeeperAdmin.html#sc_zkMulitServerSetup)

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
bigchoo@vmk1 1050 $ echo ruok | nc server1 2181
imok
bigchoo@vmk1 1048 $ echo ruok | nc vmk2 2181
imok
bigchoo@vmk1 1049 $ echo ruok | nc vmk1 2181
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
###### Zookeeper Chef
```
$ knife cookbook site download zookeeper
Downloading zookeeper from the cookbooks site at version 2.5.1 to /home/bigchoo/Cheflabs/zookeeper-2.5.1.tar.gz
Cookbook saved: /home/bigchoo/Cheflabs/zookeeper-2.5.1.tar.gz
```
* Reference
  - [Used cluster instructions from Storm setup](http://www.michael-noll.com/tutorials/running-multi-node-storm-cluster/)

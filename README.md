###### Zoo Keeper 
* Zoo keeper has been using in many application which need service discovery lookup. 

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
  * https://github.com/davidledwards/zookeeper/tree/master/zookeeper-cli
```
bigchoo@vmk2 904 $ ./zk --version
zk 1.3
```

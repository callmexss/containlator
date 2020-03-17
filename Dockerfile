FROM hub.c.163.com/public/ubuntu:16.04
COPY sources.list.xenial /etc/apt/sources.list
COPY freenet.tmp /fred
RUN mkdir /root/.pip
COPY pip.conf /root/.pip/
RUN apt-get -y update && apt-get install -y iproute2 iputils-arping net-tools tcpdump curl telnet iputils-tracepath traceroute
RUN apt-get install -y openjdk-8-jre\
                                 vim\
                                 w3m\
                                 haveged\
                                 rng-tools\
                                 fish\
                                 python3\
                                 python3-pip\
                                 tcpdump\
                                 net-tools\
                                 iputils-ping
RUN pip3 install ipython==5.5.0 pyfreenet==0.4.1 scapy
RUN adduser --disabled-password tester
RUN chown -R tester:tester /fred


RUN mv /usr/sbin/tcpdump /usr/bin/tcpdump
ENTRYPOINT /usr/sbin/sshd -D

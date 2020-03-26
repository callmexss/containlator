import os
import sys
import hashlib

import fcp


n = fcp.FCPNode()

def get_self_info(ntype="opennet-"):
    f = [x for x in os.listdir("/fred") if ntype in x and "dat" not in x].pop()

    with open(os.path.join("/fred", f)) as f:
        for line in f:
            if line.startswith("identity"):
                identity = line.strip().split("=")[1]
            if line.startswith("physical.udp"):
                address = line.strip().split("=")[1]
            if line.startswith("location"):
                location = line.strip().split("=")[1]

    return identity, address, location


def get_peers_info():
    peers_info = [(x["identity"], x["physical.udp"], x["location"]) \
            for x in n.listpeers()[:-1]]
    return peers_info


def get_opennet_relationship():
    self_info = get_self_info()
    peers_info = get_peers_info()
    return {self_info: peers_info}


def get_darknet_relationship():
    self_info = get_self_info(ntype="node-")
    peers_info = get_peers_info()
    return {self_info: peers_info}

def get_relationship(ntype):
    if ntype == "open":
        return get_opennet_relationship()
    else:
        return get_darknet_relationship()


if __name__ == "__main__":
    # res = get_self_info_open()
    # res = get_peers_info_open()
    ntype = sys.argv[1]
    res = get_relationship(ntype)
    print(res)
    

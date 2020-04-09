import os
import random
import fcp

n = fcp.FCPNode()

with open("keys.txt", "w") as f:
    for i in range(100):
        pub, pri = n.genkey()
        f.write("{}\t{}\n".format(pub, pri))
        n.put(uri=pri, data=str(random.random()))

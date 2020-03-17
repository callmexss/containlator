import sys

import fcp


def addpeer(f, Trust="LOW", Visibility="YES"):
    n = fcp.node.FCPNode(verbosity=5)
    n.addpeer(File=f, Trust=Trust, Visibility=Visibility)


if __name__ == "__main__":
    # _, f, t, v = sys.argv
    # addpeer(f, t, v)
    _, f = sys.argv
    addpeer(f)

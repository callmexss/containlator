'''
File:          dutils.py
File Created:  Tuesday, 26th November 2019 4:49:53 pm
Author:        xss (callmexss@126.com)
Description:   brief introduction
-----
Last Modified: Tuesday, 26th November 2019 5:09:40 pm
Modified By:   xss (callmexss@126.com)
-----
'''

import os
import re
import time
import random
import pickle
from collections import defaultdict

import docker


SIZE = 12
SEEDS = 1
NOD_CFG = "freenet.ini"
SED_CFG = "seed_freenet.ini"
CFG_FOLDER = "opennet-config"
BSE_NAME = "mynode"
SED_NAME = "seednode"
IMG_NAME = "tcpip1604"
IMG_VERSION = 0.3
FRIEND_RATE = 0.2


pattern = re.compile("inet addr:[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")


class Setter:
    """Config settings
    """
    def __init__(self, cfg):
        self.cfg = cfg


class DockerStarter:
    """Start docker containers
    """
    def __init__(self, size, image, version):
        """Metadata of worker

        Arguments:
            size {int} -- size of nodes
            image {str} -- image name
            version {float} -- version of image
        """
        self.size = size
        self.image = image
        self.version = version

    def create_nodes(self, basename=BSE_NAME):
        """Create freenet nodes

        Keyword Arguments:
            basename {str} -- basename of container (default: {"mynode"})
        """
        # os.system(f"rm {CFG_FOLDER}/mynode*")
        for i in range(1, self.size + 1):
            os.system(f"docker run -it --name {basename}-{i} -d {self.image}:{self.version} bash")
            os.system(f"docker cp ./exchange/dark_freenet.ini {basename}-{i}:/fred/freenet.ini")
            os.system(f"docker cp ./replaced_cfg.py {basename}-{i}:/replaced_cfg.py")
            os.system(f"docker exec -it {basename}-{i} python3 /fred/replaced_cfg.py")
            os.system(f"docker exec -it {basename}-{i} /fred/start.sh")


class DockerWorker:
    def __init__(self):
        self.client = docker.from_env()

    def get_containers_with_name(self):
        return {c.name: c for c in self.client.containers.list()}

    def get_container_by_name(self, name):
        return self.get_containers_with_name()[name]

    def get_containers(self):
        return self.client.containers.list()

    def run_cmd(self, c, cmd):
        output = c.exec_run(cmd).output.decode()
        return output

    def get_seednode_file_from_container_to_host(self, name):
        c = self.get_container_by_name(name)
        # res = c.exec_run("python3 -m http.server", detach=True)
        # ip = c.attrs["NetworkSettings"]["IPAddress"]
        # res = re.findall(pattern, c.exec_run("ifconfig").output.decode())[0]
        # url = f"http://{res.split(':')[1]}:8888/strangers/myref.txt"
        # wb_data = requests.get(url).text
        # print(wb_data)
        # print("search:", re.search(reg, wb_data).group())
        # ref = re.search(reg, wb_data).group()
        # os.system(f"wget {url} -O {CFG_FOLDER}/{name}.txt")
        c.exec_run("wget http://127.0.0.1:8888/strangers/myref.txt -O /fred/myref.fref")
        os.system(f"docker cp {c.name}:/fred/myref.fref {CFG_FOLDER}/{c.name}.txt")
        os.system(f"cat {CFG_FOLDER}/{c.name}.txt > seednodes.fref")

    def get_node_file_from_container_to_host(self, name, cfg="darknet-config"):
        c = self.get_container_by_name(name)
        c.exec_run("wget http://127.0.0.1:8888/friends/myref.txt -O /fred/myref-dark.fref")
        os.system(f"docker cp {c.name}:/fred/myref-dark.fref {cfg}/{c.name}.txt")

    def send_node_files_to_container(self, cfg="darknet-config"):
        for name in self.get_containers_with_name():
            os.system(f"docker cp {cfg} {name}:/fred/")

    def get_all_node_files(self):
        containers = self.get_containers_with_name()
        for name in containers:
            print(name)
            self.get_node_file_from_container_to_host(name)

    def get_all_seednode_files(self):
        containers = self.get_containers_with_name()
        for name in containers:
            if f'{SED_NAME}' in name:
                print(name)
                self.get_seednode_file_from_container_to_host(name)

    def send_seednode_file_to_container(self, cfg=CFG_FOLDER):
        for name in self.get_containers_with_name():
            os.system(f"docker cp {cfg} {name}:/fred/")

    # FIXME: seednodes.fref has only one `END`
    def choose_and_start_seednodes(self):
        seeds = random.sample(self.client.containers.list(), SEEDS)
        for i, seed in enumerate(seeds):
            os.system(f"docker cp {SED_CFG} {seeds[i].name}:/fred/freenet.ini")
            os.system(f"docker cp replaced_cfg.py {seeds[i].name}:/fred/bootstrap.py")
            os.system(f"docker exec -it {seeds[i].name} python3 /fred/replaced_cfg.py")
            os.system(f"docker exec -it {seeds[i].name} /fred/start.sh")
            time.sleep(5)
            seeds[i].rename(f"{seeds[i].name}-{SED_NAME}")

    def start_ordinary_nodes(self, ntype="open"):
        containers = self.get_containers_with_name()
        for name in containers:
            if f'{SED_NAME}' not in name:
                print(name)
                os.system(f"docker cp exchange/{ntype}_freenet.ini {name}:/fred/freenet.ini")
                os.system(f"docker cp seednodes.fref {name}:/fred/seednodes.fref")
                os.system(f"docker cp replaced_cfg.py {name}:/fred/replaced_cfg.py")
                # os.system(f"docker exec -it {name} cat /fred/seednodes.fref")
                os.system(f"docker exec -it {name} python3 /fred/replaced_cfg.py")
                os.system(f"docker exec -it {name} /fred/start.sh")
        time.sleep(10)

    def copy_seednodes_fref(self):
        # for each in os.listdir(f"{CFG_FOLDER}"):
            # continue
            # os.system(f"cat ./{CFG_FOLDER}/{each} >> ./{CFG_FOLDER}/seednodes.fref")
        containers = self.client.containers.list()
        for container in containers:
            print(f"Copy seednodes.fref to {container.name}")
            os.system(f"docker cp {CFG_FOLDER}/seednodes.fref {container.name}:/fred/seednodes.fref")

    def stop_all(self):
        containers = self.client.containers.list()
        for container in containers:
            print(f"Shutdown freenet in {container.name}")
            os.system(f'docker exec -it {container.name} /bin/su -c "/fred/run.sh stop" - tester')

    def connect(self, model, cfg="darknet-config"):
        for src, dsts in model.items():
            for dst in dsts:
                res = src.exec_run(f"python3 /fred/addpeer.py /fred/{cfg}/{dst.name}.txt")
                print(res)
                res = dst.exec_run(f"python3 /fred/addpeer.py /fred/{cfg}/{src.name}.txt")
                print(res)
                time.sleep(1)

    def opennet_start(self):
        self.choose_and_start_seednodes()
        self.get_all_seednode_files()
        self.copy_seednodes_fref()
        self.start_ordinary_nodes()

    def stop(self):
        self.stop_all()

    def darknet_start(self, create=True, model=None):
        if create:
            ds = DockerStarter(SIZE, IMG_NAME, IMG_VERSION)
            ds.create_nodes()
            time.sleep(10)
        else:
            self.start_ordinary_nodes("dark")

        self.get_all_node_files()
        self.send_node_files_to_container()
        orz = Organizer(SIZE, self.get_containers_with_name())
        model = orz.defined_model(model) if model else orz.generate_model()
        self.connect(model)

    def run_pyscript_in_all_containers(self, script, args):
        ret = []
        containers = self.get_containers_with_name()
        for name, container in containers.items():
            os.system(f"docker cp {script} {name}:/fred")
            res = self.run_cmd(container, f"python3 /fred/{os.path.split(script)[-1]} {' '.join(args)}")
            ret.append((name, eval(res)))
        return ret

    def get_opennet_typology(self):
        ret = self.run_pyscript_in_all_containers("scripts/get_peer_info.py", args=["open"])
        with open("opennet_relation.pkl", "wb") as f:
            pickle.dump(ret, f)

    def get_darknet_typology(self):
        ret = self.run_pyscript_in_all_containers("scripts/get_peer_info.py", ["dark"])
        with open("darknet_relation.pkl", "wb") as f:
            pickle.dump(ret, f)


class Organizer:
    def __init__(self, size, nodes):
        self.size = size
        self.nodes = nodes

    def generate_model(self):
        # each node must have at least one neighbor
        nodes = self.nodes
        model = defaultdict(list)
        for name, container in nodes.items():
            for other_name, other_container in nodes.items():
                if name != other_name and random.random() < FRIEND_RATE:
                    model[container].append(other_container)

        print(model)
        return model

    def defined_model(self, relationship):
        model = defaultdict(list)
        nodes = self.nodes
        print(relationship)
        for k, v in relationship.items():
            model[nodes[k]].extend([nodes[x] for x in v])
        print(model)
        return model


if __name__ == "__main__":
    os.system("rm ./opennet-config/*-seednode*")
    dw = DockerWorker()
    # dw.opennet_start()

    model = {
            "mynode-1": ["mynode-6"],
            "mynode-2": ["mynode-9", "mynode-6"],
            "mynode-3": ["mynode-8"],
            "mynode-4": ["mynode-7", "mynode-5"],
            "mynode-5": ["mynode-10", "mynode-12"],
            "mynode-6": ["mynode-3"],
            "mynode-7": ["mynode-6"],
            "mynode-8": ["mynode-5", "mynode-9"],
            "mynode-9": ["mynode-12"],
            "mynode-10": ["mynode-12"],
            "mynode-11": ["mynode-1", "mynode-3"],
            "mynode-12": ["mynode-3"],
            }

    model = {
        "mynode-1": ["mynode-6"],
        "mynode-2": ["mynode-6"],
        "mynode-3": ["mynode-8"],
        "mynode-4": ["mynode-7"],
        "mynode-5": ["mynode-10"],
        "mynode-6": ["mynode-3"],
        "mynode-7": ["mynode-6"],
        "mynode-8": ["mynode-4"],
        "mynode-9": ["mynode-8"],
        "mynode-10": ["mynode-12"],
        "mynode-11": ["mynode-1"],
        "mynode-12": ["mynode-3"],
    }

    # dw.darknet_start(create=False)
    dw.darknet_start(model=model)

    # dw.get_all_seednode_files()
    # dw.copy_seednodes_fref()
    # dw.start_ordinary_nodes()
    # dw.stop_all()

    # dw.get_all_node_files()
    # dw.send_node_files_to_container()
    # orz = Organizer(SIZE, dw.get_containers_with_name())
    # model = orz.generate_model()
    # dw.connect(model)

    # dw.get_opennet_typology()
    dw.get_darknet_typology()


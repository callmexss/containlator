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
from collections import defaultdict

import docker


SIZE = 20
SEEDS = 1
NOD_CFG = "freenet.ini"
SED_CFG = "seed_freenet.ini"
CFG_FOLDER = "opennet-config"
BSE_NAME = "mynode"
SED_NAME = "seednode"
IMG_VERSION = 0.4
FRIEND_RATE = 0.3


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


class DockerWorker:
    def __init__(self):
        self.client = docker.from_env()

    def get_containers_with_name(self):
        return {c.name: c for c in self.client.containers.list()}

    def get_container_by_name(self, name):
        return self.get_containers_with_name()[name]

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

    def get_all_seednode_files(self):
        containers = self.get_containers_with_name()
        for name in containers:
            if f'{SED_NAME}' in name:
                print(name)
                self.get_seednode_file_from_container_to_host(name)

    def send_seednode_file_to_container(self, cfg=CFG_FOLDER):
        for name in self.get_containers_with_name():
            os.system(f"docker cp {cfg} {name}:/fred/")

    def choose_and_start_seednodes(self):
        seeds = random.sample(self.client.containers.list(), SEEDS)
        for i, seed in enumerate(seeds):
            os.system(f"docker cp {SED_CFG} {seeds[i].name}:/fred/freenet.ini")
            os.system(f"docker cp bootstrap.py {seeds[i].name}:/fred/bootstrap.py")
            os.system(f"docker exec -it {seeds[i].name} python3 /fred/bootstrap.py")
            os.system(f"docker exec -it {seeds[i].name} /fred/start.sh")
            time.sleep(5)
            seeds[i].rename(f"{seeds[i].name}-{SED_NAME}")

    def start_ordinary_nodes(self):
        containers = self.get_containers_with_name()
        for name in containers:
            if f'{SED_NAME}' not in name:
                print(name)
                os.system(f"docker cp freenet.tmp/freenet.ini {name}:/fred/freenet.ini")
                os.system(f"docker cp seednodes.fref {name}:/fred/seednodes.fref")
                os.system(f"docker cp bootstrap.py {name}:/fred/bootstrap.py")
                # os.system(f"docker exec -it {name} cat /fred/seednodes.fref")
                os.system(f"docker exec -it {name} python3 /fred/bootstrap.py")
                os.system(f"docker exec -it {name} /fred/start.sh")
                time.sleep(5)

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


if __name__ == "__main__":
    os.system("rm ./opennet-config/*-seednode*")
    dw = DockerWorker()
    # dw.choose_and_start_seednodes()
    dw.get_all_seednode_files()
    dw.copy_seednodes_fref()
    dw.start_ordinary_nodes()
    # dw.stop_all()

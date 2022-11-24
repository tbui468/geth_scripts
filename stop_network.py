import subprocess
import time

def stop_process(port, prot):
    p = subprocess.Popen("fuser " + port + "/" + prot, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output = p.stdout.read()
    if len(str(output)) > 3: #not sure why no pid length is 3 instead of 0
        l = str(output).split()
        pid = l[1][:-1]
        subprocess.run("kill -9 " + pid, shell=True)


def stop_all():
    #stop all processes on ports used for network
    stop_process("30305", "udp") #bootstrap
    stop_process("30306", "tcp") #node 1
    stop_process("30307", "tcp")
    stop_process("30308", "tcp") #node2
    stop_process("30309", "tcp")
    stop_process("30310", "tcp") #miner
    stop_process("30311", "tcp")

stop_all()

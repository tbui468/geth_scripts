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
    stop_process("30305", "udp") #bootstrap node
    stop_process("30306", "tcp") #node 1 execution client
    stop_process("30307", "tcp") #node 1 consensus client (not used)
    stop_process("30308", "tcp") #node 2 execution client
    stop_process("30309", "tcp") #node 2 consensus client (not used)
    stop_process("30310", "tcp") #node 3 execution client
    stop_process("30311", "tcp") #node 3 consensus client (not used)
    stop_process("8545", "tcp") #json-rpc server on node 1

stop_all()

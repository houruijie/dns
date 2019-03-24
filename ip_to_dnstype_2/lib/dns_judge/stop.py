import os
import signal


def stop():
    def check_pid(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    with open('./gid.txt', 'r') as f:
        gid = int(f.read())
        print("Gid in file:"+str(gid))

    if check_pid(gid):
        os.killpg(gid,signal.SIGKILL)
        print("Kill the service sucessully")
    else:
        print("No such process group")

if __name__ == '__main__':
    stop()
import subprocess
import shlex
import time
from sys import stdout


def record_agqr(p):
    cmd = "/usr/bin/rtmpdump"
    url = "rtmp://fms-base1.mitene.ad.jp/agqr/aandg22"
    cmdopt = {
        "-r": url,
        "--live": None,
        "-B": p["length"],
        }
    cmds = [cmd, ] + [_ for c in cmdopt.items() for _ in c if _]
    p = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
#    try:
#        while True:
#            time.sleep(1)
#            if p.poll() is not None:
#                print(p.communicate())
#                break
#    except:
#        p.terminate()

if __name__ == '__main__':
    record_agqr({"length": "10"})
    print("complete!")

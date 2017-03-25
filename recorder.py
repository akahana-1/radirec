import subprocess
import shlex
import time


def record_agqr(p):
    cmd = "/usr/bin/rtmpdump"
    url = "rtmp://fms-base1.mitene.ad.jp/agqr/aandg22"
    cmdopt = {
        "-r": url,
        "--live": None,
        "-B": p["length"],
        "-o": "hoge.flv"
        }
    cmds = [cmd, ] + [_ for c in cmdopt.items() for _ in c if _]
    p = subprocess.Popen(cmds, stderr=subprocess.DEVNULL)

if __name__ == '__main__':
    record_agqr({"length": "100"})
    print("complete!")

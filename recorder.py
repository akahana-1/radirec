import subprocess
import shlex


def record_agqr(p):
    cmd = "/usr/bin/rtmpdump -r {url} --live -B {length} -o {file}"
    url = "rtmp://fms-base1.mitene.ad.jp/agqr/aandg22"
    cmdopt = {
        "length": p["length"],
        "file": "hoge.flv"
        }
    cmds = shlex.split(cmd.format(url=url, **cmdopt))
    p = subprocess.Popen(cmds, stderr=subprocess.DEVNULL)


def record_chofu(p):
    cmd = "/usr/bin/ffmpeg -i {url} -t {length} {file}"
    url = "mmsh://hdv3.nkansai.tv/chofu?MSWMExt=.asf"
    cmdopt = {
            "length": p["length"],
            "file": "fuga.mp3"
            }
    cmds = shlex.split(cmd.format(url=url, **cmdopt))
    p = subprocess.Popen(cmds, stderr=subprocess.DEVNULL)

if __name__ == '__main__':
    record_agqr({"length": "30"})
    record_chofu({"length": "30"})
    print("complete!")

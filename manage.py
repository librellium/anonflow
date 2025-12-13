import os
import subprocess
import sys

from anonflow import __version_str__

def main():
    os.environ["VERSION"] = __version_str__
    subprocess.check_call(["docker", "compose"] + sys.argv[1:])

if __name__ == "__main__":
    main()

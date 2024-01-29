import sys
from winutils.clear_ram import core

if len(sys.argv) == 1:
    core.quit_apps()
elif len(sys.argv) == 2 and sys.argv[1] == "-s":
    core.start_apps()

import time
from winutils.mechvibes_volume import core


core.Handler.start()
while True:
    time.sleep(1e6)

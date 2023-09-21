from winutils.monitor_brightness import core
from winutils._helpers import overlay

core.Handler.start(suppress=False)
overlay.root.mainloop()

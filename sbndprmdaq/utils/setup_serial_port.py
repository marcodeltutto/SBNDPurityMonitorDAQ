# This script has the effect of making DTR and RTS pins not
# being affected from the port being opened or closed,
# so they can be used as GPIO pins.

import termios

paths = [
    '/dev/ttyS0',
    '/dev/ttyS1',
    '/dev/ttyS2',
]

for path in paths:
    with open(path) as f:
        attrs = termios.tcgetattr(f)
        attrs[2] = attrs[2] & ~termios.HUPCL
        termios.tcsetattr(f, termios.TCSAFLUSH, attrs)
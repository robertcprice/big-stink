#!/usr/bin/env python3
"""ASCII ocean wave animation for the terminal."""
import math, time, os, sys, signal

COLS = min(os.get_terminal_size().columns, 110)
ROWS = min(os.get_terminal_size().lines - 2, 34)

DEEP   = [' ', ' ', '.', '·']
MID    = ['~', '~', '-', '≈']
SURF   = ['≈', '≋', '∽', '∿', '~']
FOAM   = ["'", '"', '`', '*', '°', '˚']
WASH   = ['.', ',', '·', ':', ';', "'"]
SAND   = ['▓', '▒', '░']

# ANSI 256-color codes
C_BG     = '\033[48;2;10;10;26m'
C_RESET  = '\033[0m'
C_HIDE   = '\033[?25l'
C_SHOW   = '\033[?25h'

def rgb(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

DEEP_C  = [rgb(11,37,69),  rgb(13,48,96),  rgb(15,59,122)]
MID_C   = [rgb(26,90,138), rgb(32,112,160), rgb(40,136,187)]
SURF_C  = [rgb(58,159,216), rgb(80,176,232), rgb(106,196,240)]
FOAM_C  = [rgb(200,230,245), rgb(223,240,250), rgb(255,255,255)]
WASH_C  = [rgb(138,184,208), rgb(160,204,224), rgb(184,221,239)]
SAND_C  = [rgb(194,168,120), rgb(184,152,96), rgb(212,188,138)]
STAR_C  = rgb(68, 85, 102)

def pick(arr, i):
    return arr[abs(int(i)) % len(arr)]

def noise(x, y, t):
    v  = math.sin(x * 0.07 + t * 0.6)
    v += math.sin(x * 0.13 - t * 0.4 + y * 0.1) * 0.7
    v += math.sin(x * 0.21 + t * 0.9 + y * 0.05) * 0.4
    v += math.sin(y * 0.3 + t * 0.3) * 0.5
    v += math.sin((x + y) * 0.05 + t * 0.2) * 0.8
    return v

def render(t):
    buf = []
    shore_base = ROWS * 0.78
    shore_wave = math.sin(t * 0.15) * 2

    for y in range(ROWS):
        line = []
        for x in range(COLS):
            n = noise(x, y, t)
            shore_off = math.sin(x * 0.05 + t * 0.2) * 3 + shore_wave
            shore_y = shore_base + shore_off
            wash_ext = math.sin(t * 0.3 + x * 0.04) * 2.5 + math.sin(t * 0.7) * 1.5
            wash_y = shore_y + wash_ext + 1

            if y < ROWS * 0.08:
                s = math.sin(x * 7.7 + y * 13.3 + t * 0.1)
                if s > 0.97:
                    line.append(STAR_C + '.')
                else:
                    line.append(' ')
            elif y < ROWS * 0.15:
                hn = math.sin(x * 0.1 + t * 0.3) + math.sin(x * 0.23 - t * 0.2) * 0.5
                if hn > 0.8:
                    line.append(pick(DEEP_C, x) + pick(MID, x + int(t * 2)))
                else:
                    line.append(pick(DEEP_C, int(n * 3)) + pick(DEEP, int(n * 10 + x)))
            elif y < ROWS * 0.4:
                intensity = n * 0.5 + 0.5
                if intensity > 0.75:
                    line.append(pick(MID_C, int(n * 5)) + pick(MID, int(n * 10 + x + t * 3)))
                elif intensity > 0.4:
                    line.append(pick(DEEP_C, int(n * 4)) + pick(DEEP, int(n * 8 + x)))
                else:
                    line.append(' ')
            elif y < shore_y - 4:
                intensity = n * 0.5 + 0.5
                if intensity > 0.7:
                    line.append(pick(SURF_C, int(n * 5)) + pick(SURF, int(n * 10 + x + t * 5)))
                elif intensity > 0.35:
                    line.append(pick(MID_C, int(n * 4)) + pick(MID, int(n * 8 + x + t * 3)))
                else:
                    line.append(pick(DEEP_C, int(n * 3)) + pick(DEEP, int(n * 6 + x)))
            elif y < shore_y:
                sn = noise(x * 1.5, y, t * 1.4)
                bp = math.sin(x * 0.08 + t * 0.8 - y * 0.3)
                close = 1 - (shore_y - y) / 4
                if bp > 0.3 and close > 0.4:
                    line.append(pick(FOAM_C, int(sn * 4)) + pick(FOAM, int(sn * 10 + t * 6)))
                elif sn > 0:
                    line.append(pick(SURF_C, int(sn * 5)) + pick(SURF, int(sn * 10 + x + t * 4)))
                else:
                    line.append(pick(MID_C, int(sn * 3 + 1)) + pick(MID, int(sn * 6 + x)))
            elif y < wash_y:
                wn = noise(x * 1.2, y * 2, t * 1.2)
                fade = 1 - (y - shore_y) / max(wash_y - shore_y, 0.01)
                if fade > 0.5 and wn > -0.3:
                    line.append(pick(WASH_C, int(wn * 3 + fade * 2)) + pick(WASH, int(wn * 10 + t * 4)))
                elif fade > 0.2:
                    line.append(pick(WASH_C, 2) + pick(['.', ' ', '·', ' '], int(wn * 5 + x)))
                else:
                    line.append(pick(SAND_C, int(x * 0.2)) + pick(SAND, int(x * 0.3 + y)))
            else:
                sn = math.sin(x * 0.5 + y * 0.8) * 0.5 + 0.5
                line.append(pick(SAND_C, int(sn * 3 + y)) + pick(SAND, int(sn * 3)))

        buf.append(''.join(line))

    return '\n'.join(buf) + C_RESET

def cleanup(*_):
    sys.stdout.write(C_SHOW + C_RESET + '\033[2J\033[H')
    sys.stdout.flush()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

sys.stdout.write(C_HIDE + '\033[2J')
sys.stdout.flush()

t = 0.0
try:
    while True:
        frame = render(t)
        sys.stdout.write('\033[H' + C_BG + frame)
        sys.stdout.flush()
        t += 0.06
        time.sleep(0.045)
except KeyboardInterrupt:
    cleanup()

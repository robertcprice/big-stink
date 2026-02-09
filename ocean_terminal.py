#!/usr/bin/env python3
"""3D perspective ASCII ocean - raycasted view looking out over water."""
import math, time, os, sys, signal

COLS = min(os.get_terminal_size().columns, 120)
ROWS = min(os.get_terminal_size().lines - 1, 45)
HORIZON = int(ROWS * 0.38)
CAM_HEIGHT = 3.0
FOCAL = 60.0

C_RESET = '\033[0m'
C_HIDE  = '\033[?25l'
C_SHOW  = '\033[?25h'

def rgb_fg(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

def rgb_bg(r, g, b):
    return f'\033[48;2;{r};{g};{b}m'

def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t

def lerp_c(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (int(lerp(c1[0], c2[0], t)),
            int(lerp(c1[1], c2[1], t)),
            int(lerp(c1[2], c2[2], t)))

# Palettes
SKY_TOP   = (5, 5, 20)
SKY_MID   = (15, 20, 50)
SKY_HOR   = (40, 55, 85)
W_DEEP    = (8, 30, 60)
W_MID     = (20, 70, 120)
W_LIGHT   = (50, 140, 200)
W_BRIGHT  = (100, 190, 240)
FOAM_C    = (210, 235, 250)
WHITE     = (255, 255, 255)
FOG_C     = (12, 25, 50)

FLAT    = [' ', ' ', '.', '\u00b7', ' ', '.']
GENTLE  = ['~', '~', '-', '~', '\u2248', '-']
MEDIUM  = ['\u2248', '\u223f', '~', '\u2248', '\u223d', '\u224b']
STEEP   = ['\u2593', '\u2592', '\u2591', '\u2588', '\u2593', '\u2592']
CREST   = ["'", '"', '`', '^', '\u00b0', '*']
FOAM    = ['\u2591', '\u2592', '\u00b7', ':', '.', "'"]

def pick(arr, i):
    return arr[abs(int(i)) % len(arr)]

def wave_h(wx, wz, t):
    h  = math.sin(wz * 0.4 + t * 0.8)
    h += math.sin(wz * 0.15 + wx * 0.05 + t * 0.5) * 0.6
    h += math.sin(wx * 0.3 + wz * 0.2 - t * 0.6) * 0.35
    h += math.sin(wx * 0.12 - t * 0.3) * 0.2
    h += math.sin(wx * 0.8 + wz * 0.9 + t * 1.5) * 0.15
    h += math.sin(wx * 1.5 - wz * 0.7 + t * 2.0) * 0.08
    return h

def wave_slope(wx, wz, t):
    e = 0.3
    dx = (wave_h(wx + e, wz, t) - wave_h(wx - e, wz, t)) / (2 * e)
    dz = (wave_h(wx, wz + e, t) - wave_h(wx, wz - e, t)) / (2 * e)
    return dx, dz

def render(t):
    buf = []
    for row in range(ROWS):
        line = []
        if row <= HORIZON:
            # Sky
            st = row / max(HORIZON, 1)
            if st < 0.5:
                sc = lerp_c(SKY_TOP, SKY_MID, st * 2)
            else:
                sc = lerp_c(SKY_MID, SKY_HOR, (st - 0.5) * 2)

            for col in range(COLS):
                ch = ' '
                color = sc
                # Stars
                seed = math.sin(col * 127.1 + row * 311.7) * 43758.5453
                sv = seed - math.floor(seed)
                if sv > 0.992 and st < 0.7:
                    tw = math.sin(t * 0.5 + col * 3.7 + row * 2.3) * 0.5 + 0.5
                    br = int(80 + tw * 120)
                    ch = '*' if sv > 0.997 else '.'
                    color = (br, br, min(255, br + 40))
                # Moon
                mx, my = COLS * 0.75, HORIZON * 0.25
                md = math.sqrt((col - mx)**2 + (row - my)**2)
                if md < 2:
                    ch = 'O' if md < 1 else '\u00b7'
                    color = (220, 220, 200)
                elif md < 10:
                    g = 1 - md / 10
                    color = lerp_c(sc, (60, 60, 80), g * 0.4)
                # Horizon glow
                if row >= HORIZON - 2:
                    gt = 1 - (HORIZON - row) / 2
                    hg = math.sin(col * 0.05 + t * 0.1) * 0.1 + 0.15
                    color = lerp_c(color, (60, 70, 100), gt * hg)
                line.append((ch, color))
        else:
            # Water - 3D perspective
            sd = row - HORIZON
            wz = (CAM_HEIGHT * FOCAL) / sd
            ps = wz / FOCAL
            for col in range(COLS):
                wx = (col - COLS / 2) * ps
                h = wave_h(wx, wz, t)
                dx, dz = wave_slope(wx, wz, t)
                sm = math.sqrt(dx * dx + dz * dz)
                df = min(1.0, wz / 80)
                sun = math.sin(t * 0.05) * 0.3
                spec = max(0, dx * sun + dz * 0.5)
                sp = (spec ** 3) * (1 - df * 0.5)

                near_crest = h > 0.8 and dz < -0.2
                breaking = h > 1.2 and sm > 0.8 and wz < 20

                if breaking:
                    ch = pick(FOAM, h * 10 + wx * 3 + t * 4)
                elif near_crest:
                    ch = pick(CREST, wx * 2 + t * 3)
                elif df > 0.7:
                    i = h * 4 + wx * 0.5 + t
                    ch = pick(GENTLE, i) if sm > 0.3 else pick(FLAT, i)
                elif sm > 0.7:
                    ch = pick(STEEP, h * 8 + wx * 2 + t * 3)
                elif sm > 0.3:
                    ch = pick(MEDIUM, h * 6 + wx + t * 2)
                else:
                    i = h * 4 + wx * 0.5 + t
                    ch = pick(GENTLE, i) if sm > 0.15 else pick(FLAT, i)

                hn = (h + 2) / 4
                if hn > 0.7:
                    bc = lerp_c(W_LIGHT, W_BRIGHT, (hn - 0.7) / 0.3)
                elif hn > 0.4:
                    bc = lerp_c(W_MID, W_LIGHT, (hn - 0.4) / 0.3)
                else:
                    bc = lerp_c(W_DEEP, W_MID, hn / 0.4)

                if sp > 0.1:
                    bc = lerp_c(bc, WHITE, sp * 0.6)
                if breaking:
                    bc = lerp_c(bc, FOAM_C, 0.7)
                elif near_crest:
                    bc = lerp_c(bc, FOAM_C, 0.4)
                bc = lerp_c(bc, FOG_C, df * 0.75)

                # Moon reflection
                mrx = COLS * 0.75
                rd = abs(col - mrx)
                rw = 3 + wz * 0.15
                if rd < rw:
                    rs = (1 - rd / rw) * (0.2 + 0.15 * math.sin(wz * 0.5 + t))
                    sh = math.sin(wx * 2 + wz * 0.8 + t * 2) * 0.5 + 0.5
                    bc = lerp_c(bc, (200, 200, 180), rs * sh * 0.6)
                    if rs * sh > 0.25 and rd < rw * 0.5:
                        ch = '|' if sh > 0.6 else ':'

                line.append((ch, bc))
        buf.append(line)
    return buf

def frame_to_str(buf):
    out = []
    for line in buf:
        parts = []
        pc = None
        for ch, c in line:
            if c != pc:
                parts.append(rgb_fg(c[0], c[1], c[2]))
                pc = c
            parts.append(ch)
        out.append(''.join(parts))
    return '\n'.join(out) + C_RESET

def cleanup(*_):
    sys.stdout.write(C_SHOW + C_RESET + '\033[2J\033[H')
    sys.stdout.flush()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

sys.stdout.write(C_HIDE + '\033[2J')
sys.stdout.flush()

t = 0.0
BG = rgb_bg(0, 0, 0)
try:
    while True:
        frame = render(t)
        sys.stdout.write('\033[H' + BG + frame_to_str(frame))
        sys.stdout.flush()
        t += 0.05
        time.sleep(0.04)
except KeyboardInterrupt:
    cleanup()

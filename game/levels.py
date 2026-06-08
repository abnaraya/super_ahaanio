import random as _rng

from game.constants import HEIGHT, LEVEL_END_X
from game.objects import Platform, MovingPlatform, Coin, Pipe, Flag, PowerUp
from game.enemies import Enemy
from game.boss import Boss, Mom


def _ground_with_pits(level_num, level_end_x=LEVEL_END_X):
    """Build ground segments with gaps (bottomless pits).

    Returns a list of Platform objects forming the ground.
    Level 1 has no pits (safe intro). Higher levels get more/wider pits.
    Boss and secret levels use a solid ground (no pits).
    """
    if level_num <= 1:
        return [Platform(0, HEIGHT - 50, level_end_x + 200, 50)]

    # Seeded so the same level always has the same pits
    rng = _rng.Random(level_num * 7 + 3)
    num_pits = min(2 + (level_num - 2) // 2, 5)
    pit_width_min = 100
    pit_width_max = min(120 + level_num * 10, 250)

    segments = []
    x = 0
    # Reserve safe zones: start (0-250), flag area (end-200 to end), pipe positions
    safe_zones = [(0, 280), (level_end_x - 200, level_end_x + 200)]
    pit_positions = []

    # Generate pit positions avoiding safe zones
    attempts = 0
    while len(pit_positions) < num_pits and attempts < 50:
        attempts += 1
        pit_x = rng.randint(300, level_end_x - 300)
        pit_w = rng.randint(pit_width_min, pit_width_max)
        # Check safe zones
        overlaps = False
        for sz_start, sz_end in safe_zones:
            if pit_x < sz_end and pit_x + pit_w > sz_start:
                overlaps = True
                break
        for px, pw in pit_positions:
            if abs(pit_x - px) < pw + 200:  # min 200px between pits
                overlaps = True
                break
        if not overlaps:
            pit_positions.append((pit_x, pit_w))

    pit_positions.sort()

    # Build ground segments around pits
    cursor = 0
    for pit_x, pit_w in pit_positions:
        if pit_x > cursor:
            segments.append(Platform(cursor, HEIGHT - 50, pit_x - cursor, 50))
        cursor = pit_x + pit_w
    if cursor < level_end_x + 200:
        segments.append(Platform(cursor, HEIGHT - 50, level_end_x + 200 - cursor, 50))

    return segments


def create_normal_level(level_num=1):
    if level_num == 5:
        elevated = [
            Platform(200, 420, 120, 20),
            Platform(400, 350, 100, 20),
            MovingPlatform(580, 280, 80, 20, "vertical", 60, 1.5),
            Platform(750, 380, 140, 20),
            MovingPlatform(950, 320, 100, 20, "horizontal", 80, 2),
            Platform(1150, 250, 120, 20),
            MovingPlatform(1350, 400, 100, 20, "vertical", 70, 1),
            Platform(1550, 330, 110, 20),
            MovingPlatform(1750, 280, 120, 20, "horizontal", 100, 1.5),
            Platform(1950, 390, 150, 20),
        ]
        platforms = _ground_with_pits(level_num) + elevated
        enemies = [
            Enemy(220, 420 - 34, "badminton", elevated[0].rect),
            Enemy(420, 350 - 34, "badminton", elevated[1].rect),
            Enemy(770, 380 - 34, "badminton", elevated[3].rect),
            Enemy(1170, 250 - 34, "badminton", elevated[5].rect),
            Enemy(1570, 330 - 34, "badminton", elevated[7].rect),
            Enemy(1970, 390 - 34, "badminton", elevated[9].rect),
        ]
        coins = [
            Coin(250, 400), Coin(280, 400), Coin(310, 400),
            Coin(450, 330), Coin(480, 330),
            Coin(620, 260), Coin(650, 260),
            Coin(800, 360), Coin(830, 360), Coin(860, 360),
            Coin(1000, 300), Coin(1030, 300),
            Coin(1200, 230), Coin(1230, 230), Coin(1260, 230),
            Coin(1400, 380), Coin(1430, 380),
            Coin(1600, 310), Coin(1630, 310), Coin(1660, 310),
            Coin(1800, 260), Coin(1830, 260),
            Coin(2000, 370), Coin(2030, 370), Coin(2060, 370),
        ]
        powerups = [
            PowerUp(350, 400, 'nintendo'),
            PowerUp(540, 330, 'drums'),
            PowerUp(890, 360, 'soccer'),
            PowerUp(1100, 300, 'life'),
            PowerUp(1300, 230, 'speed'),
            PowerUp(1500, 310, 'jump'),
            PowerUp(1890, 370, 'nintendo'),
        ]
        pipes = [
            Pipe(120, HEIGHT - 120, 60, 70),
            Pipe(500, HEIGHT - 120, 60, 70, is_warp_pipe=True),
            Pipe(1000, HEIGHT - 120, 60, 70),
            Pipe(1450, HEIGHT - 120, 60, 70, is_warp_pipe=True),
            Pipe(1850, HEIGHT - 120, 60, 70),
        ]
        flag = Flag(LEVEL_END_X + 35, HEIGHT - 50)
        mom = None
        return platforms, enemies, coins, pipes, flag, powerups, mom

    level_pattern = level_num % 4

    if level_pattern == 1:
        elevated = [
            Platform(250, 450, 100, 20),
            Platform(450, 380, 120, 20),
            MovingPlatform(650, 320, 80, 20, "vertical", 80, 1),
            Platform(850, 280, 140, 20),
            MovingPlatform(1100, 350, 100, 20, "horizontal", 120, 2),
            Platform(1350, 420, 120, 20),
            MovingPlatform(1600, 380, 100, 20, "vertical", 60, 1.5),
            Platform(1850, 320, 120, 20),
        ]
        platforms = _ground_with_pits(level_num) + elevated
        enemies = [
            Enemy(270, 450 - 34, "homework", elevated[0].rect),
            Enemy(470, 380 - 34, "homework", elevated[1].rect),
            Enemy(870, 280 - 34, "homework", elevated[3].rect),
            Enemy(1370, 420 - 34, "homework", elevated[5].rect),
        ]
        coins = [
            Coin(300, 430), Coin(500, 360), Coin(700, 300),
            Coin(900, 260), Coin(1150, 330), Coin(1400, 400), Coin(1650, 360),
        ]
        powerups = [
            PowerUp(380, 450, 'nintendo'),
            PowerUp(720, 300, 'drums'),
            PowerUp(980, 260, 'soccer'),
            PowerUp(1520, 360, 'speed'),
        ]

    elif level_pattern == 2:
        elevated = [
            Platform(200, 420, 140, 20),
            MovingPlatform(400, 350, 100, 20, "horizontal", 100, 1.5),
            Platform(600, 280, 120, 20),
            MovingPlatform(800, 400, 100, 20, "vertical", 70, 1),
            Platform(1000, 320, 140, 20),
            Platform(1250, 380, 100, 20),
            MovingPlatform(1450, 300, 120, 20, "horizontal", 80, 2),
            Platform(1700, 420, 140, 20),
        ]
        platforms = _ground_with_pits(level_num) + elevated
        enemies = [
            Enemy(220, 420 - 34, "chores", elevated[0].rect),
            Enemy(820, 400 - 34, "chores", elevated[3].rect),
            Enemy(1020, 320 - 34, "chores", elevated[4].rect),
            Enemy(1270, 380 - 34, "chores", elevated[5].rect),
        ]
        coins = [
            Coin(270, 400), Coin(450, 330), Coin(650, 260),
            Coin(850, 380), Coin(1100, 300), Coin(1300, 360), Coin(1550, 280),
        ]
        powerups = [
            PowerUp(320, 400, 'drums'),
            PowerUp(680, 260, 'nintendo'),
            PowerUp(1180, 300, 'jump'),
            PowerUp(1620, 400, 'life'),
        ]

    elif level_pattern == 3:
        elevated = [
            Platform(300, 400, 80, 20),
            MovingPlatform(480, 320, 100, 20, "vertical", 60, 1.5),
            Platform(680, 240, 80, 20),
            MovingPlatform(880, 360, 120, 20, "horizontal", 100, 1),
            Platform(1100, 280, 100, 20),
            Platform(1350, 400, 140, 20),
            MovingPlatform(1600, 320, 100, 20, "circular", 60, 1),
            Platform(1800, 380, 120, 20),
        ]
        platforms = _ground_with_pits(level_num) + elevated
        enemies = [
            Enemy(320, 400 - 34, "badminton", elevated[0].rect),
            Enemy(700, 240 - 34, "badminton", elevated[2].rect),
            Enemy(1120, 280 - 34, "badminton", elevated[4].rect),
            Enemy(1820, 380 - 34, "badminton", elevated[7].rect),
        ]
        coins = [
            Coin(340, 380), Coin(520, 300), Coin(720, 220),
            Coin(920, 340), Coin(1140, 260), Coin(1400, 380), Coin(1640, 300),
        ]
        powerups = [
            PowerUp(580, 300, 'soccer'),
            PowerUp(760, 220, 'nintendo'),
            PowerUp(1020, 340, 'drums'),
            PowerUp(1720, 360, 'speed'),
        ]

    else:
        elevated = [
            Platform(180, 450, 90, 15),
            Platform(350, 380, 70, 15),
            Platform(520, 320, 100, 15),
            Platform(720, 280, 80, 15),
            Platform(900, 370, 110, 15),
            Platform(1150, 300, 90, 15),
            Platform(1350, 420, 120, 15),
            Platform(1550, 350, 100, 15),
            Platform(1750, 400, 140, 15),
        ]
        platforms = _ground_with_pits(level_num) + elevated
        enemies = [
            Enemy(200, 450 - 34, "shower", elevated[0].rect),
            Enemy(370, 380 - 34, "shower", elevated[1].rect),
            Enemy(540, 320 - 34, "shower", elevated[2].rect),
            Enemy(920, 370 - 34, "shower", elevated[4].rect),
            Enemy(1170, 300 - 34, "shower", elevated[5].rect),
            Enemy(1570, 350 - 34, "shower", elevated[7].rect),
        ]
        coins = [
            Coin(220, 430), Coin(390, 360), Coin(560, 300),
            Coin(750, 260), Coin(950, 350), Coin(1190, 280), Coin(1590, 330),
        ]
        powerups = [
            PowerUp(450, 360, 'nintendo'),
            PowerUp(820, 260, 'drums'),
            PowerUp(1070, 350, 'life'),
            PowerUp(1470, 400, 'jump'),
        ]

    pipes = [
        Pipe(170, HEIGHT - 120, 60, 70),
        Pipe(570, HEIGHT - 120, 60, 70, is_warp_pipe=True),
        Pipe(980, HEIGHT - 120, 60, 70),
        Pipe(1380, HEIGHT - 120, 60, 70, is_warp_pipe=True),
    ]
    flag = Flag(LEVEL_END_X + 35, HEIGHT - 50)
    # Mom hazard appears in levels >= 4 (non-boss)
    mom = Mom(LEVEL_END_X // 2, HEIGHT - 50) if level_num >= 4 else None
    return platforms, enemies, coins, pipes, flag, powerups, mom


def create_secret_level(secret_type=1):
    if secret_type == 1:
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X + 100, 50),
            Platform(200, 450, 120, 20), Platform(400, 380, 140, 20),
            Platform(600, 320, 100, 20), Platform(800, 260, 160, 20),
            Platform(1100, 320, 120, 20), Platform(1350, 380, 140, 20),
            Platform(1600, 300, 120, 20), Platform(1850, 420, 200, 20),
        ]
        enemies = []
        coins = [
            Coin(230, 430), Coin(260, 430), Coin(290, 430),
            Coin(430, 360), Coin(460, 360), Coin(490, 360), Coin(520, 360),
            Coin(630, 300), Coin(660, 300), Coin(690, 300),
            Coin(820, 240), Coin(850, 240), Coin(880, 240), Coin(910, 240), Coin(940, 240),
            Coin(1130, 300), Coin(1160, 300), Coin(1190, 300), Coin(1220, 300),
            Coin(1380, 360), Coin(1410, 360), Coin(1440, 360), Coin(1470, 360),
            Coin(1630, 280), Coin(1660, 280), Coin(1690, 280), Coin(1720, 280),
            Coin(1900, 400), Coin(1930, 400), Coin(1960, 400), Coin(1990, 400), Coin(2020, 400),
        ]
        powerups = [
            PowerUp(320, 430, 'nintendo'), PowerUp(520, 360, 'nintendo'),
            PowerUp(880, 240, 'drums'), PowerUp(1180, 300, 'soccer'),
            PowerUp(1420, 360, 'nintendo'), PowerUp(1670, 280, 'drums'),
            PowerUp(1950, 400, 'life'), PowerUp(750, 240, 'speed'),
            PowerUp(1250, 300, 'jump'), PowerUp(1550, 280, 'soccer'),
        ]
    elif secret_type == 2:
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X + 100, 50),
            Platform(180, 420, 100, 20), Platform(350, 350, 120, 20),
            Platform(550, 280, 140, 20), Platform(780, 380, 100, 20),
            Platform(980, 320, 120, 20), Platform(1200, 260, 100, 20),
            Platform(1400, 350, 140, 20), Platform(1650, 400, 180, 20),
        ]
        enemies = []
        coins = [
            Coin(210, 400), Coin(240, 400),
            Coin(380, 330), Coin(410, 330), Coin(440, 330),
            Coin(580, 260), Coin(610, 260), Coin(640, 260), Coin(670, 260),
            Coin(810, 360), Coin(840, 360),
            Coin(1010, 300), Coin(1040, 300), Coin(1070, 300),
            Coin(1230, 240), Coin(1260, 240),
            Coin(1430, 330), Coin(1460, 330), Coin(1490, 330),
            Coin(1700, 380), Coin(1730, 380), Coin(1760, 380), Coin(1790, 380),
        ]
        powerups = [
            PowerUp(220, 400, 'drums'), PowerUp(420, 330, 'drums'),
            PowerUp(620, 260, 'drums'), PowerUp(820, 360, 'soccer'),
            PowerUp(1020, 300, 'soccer'), PowerUp(1240, 240, 'nintendo'),
            PowerUp(1470, 330, 'soccer'), PowerUp(1750, 380, 'life'),
            PowerUp(600, 260, 'speed'), PowerUp(1100, 300, 'jump'),
        ]
    else:
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X + 100, 50),
            Platform(200, 440, 120, 20), Platform(400, 370, 100, 20),
            Platform(600, 300, 140, 20), Platform(850, 380, 120, 20),
            Platform(1100, 320, 100, 20), Platform(1300, 260, 140, 20),
            Platform(1550, 350, 120, 20), Platform(1800, 420, 200, 20),
        ]
        enemies = []
        coins = [
            Coin(230, 420), Coin(260, 420), Coin(290, 420),
            Coin(430, 350), Coin(460, 350),
            Coin(630, 280), Coin(660, 280), Coin(690, 280), Coin(720, 280),
            Coin(880, 360), Coin(910, 360), Coin(940, 360),
            Coin(1130, 300), Coin(1160, 300),
            Coin(1330, 240), Coin(1360, 240), Coin(1390, 240), Coin(1420, 240),
            Coin(1580, 330), Coin(1610, 330), Coin(1640, 330),
            Coin(1850, 400), Coin(1880, 400), Coin(1910, 400), Coin(1940, 400), Coin(1970, 400),
        ]
        powerups = [
            PowerUp(270, 420, 'speed'), PowerUp(450, 350, 'speed'),
            PowerUp(670, 280, 'speed'), PowerUp(920, 360, 'life'),
            PowerUp(1150, 300, 'nintendo'), PowerUp(1370, 240, 'life'),
            PowerUp(1370, 240, 'jump'), PowerUp(1620, 330, 'drums'),
            PowerUp(1920, 400, 'life'), PowerUp(750, 280, 'soccer'),
        ]

    pipes = [
        Pipe(100, HEIGHT - 120, 60, 70, is_warp_pipe=True),
        Pipe(LEVEL_END_X - 100, HEIGHT - 120, 60, 70, is_warp_pipe=True),
    ]
    flag = Flag(LEVEL_END_X + 35, HEIGHT - 50)
    mom = None
    return platforms, enemies, coins, pipes, flag, powerups, mom


def create_boss_level(boss_level):
    platforms = [
        Platform(0, HEIGHT - 50, LEVEL_END_X + 100, 50),
        Platform(200, 480, 120, 20), Platform(380, 420, 120, 20),
        Platform(560, 360, 120, 20), Platform(480, 250, 160, 30),
        Platform(720, 360, 120, 20), Platform(900, 420, 120, 20),
        Platform(150, 380, 80, 20), Platform(800, 300, 80, 20),
    ]
    enemies = []
    coins = [
        Coin(230, 460), Coin(410, 400), Coin(590, 340),
        Coin(750, 340), Coin(930, 400), Coin(180, 360),
    ]
    powerups = [
        PowerUp(260, 460, 'nintendo'),
        PowerUp(830, 280, 'drums'),
        PowerUp(450, 400, 'soccer'),
    ]
    pipes = []
    flag = None
    boss = Boss(520, 250 - 80, boss_level)
    return platforms, enemies, coins, pipes, flag, powerups, boss

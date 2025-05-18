import curses
import time
import random
import math

# --- Constants & Utility ---
# CHAR_SETS = {} # Not directly used in rendering path in the JS, seems like a placeholder
GAME_WIDTH = 80
GAME_HEIGHT = 45
FPS = 30  # Target frames per second

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

# --- ASCII ART ---
ASCII_ART = {
    "player": ["◀◁^°^▷▶", "▣*@#*▣", "▓░▒█░▓", "^¤°¤^"],
    "player_large": ["  ◢▆▆◣  ", " ◤║^^^║◥ ", "◀▓╬ ■ ╬▓▶", " 🛡▣@#▣🛡 ", "  ▀███▀  "],
    "powerUp_sizeIncrease": ["╭───╮", "│ S │", "╰───╯"],
    "powerUp_laserCharge": ["╭───╮", "│ L │", "╰───╯"],
    "basicEnemy": ["▲△v°v△▲", "▣*@#*▣", "░▓▒█▓░", "v¤°¤v"],
    "laserEnemy": [" <◊═◊> ", "╔═╩█╩═╗", "  ╿╿╿  "],
    "serpentHead": ["  .--.  ", " /ö_ö\\ \\ ", " \\ vv / ", "  `~~'  "],
    "serpentBody": ["╭ 形 ╮", "╞═══╡", "╰────╯"],
    "deathSymbol": ["   ╔═══╗   ", "   ║RIP║   ", "   ║   ║   ", "╔══╩═══╩══╗", "║          ║", "╚══════════╝"],
    "boss": ["^-==<[¤>><<¤]>-==^", "▓▓▒▓▒█░░░░░░░█▒▓▒▓▓", "░░█▓█░▒▓▓▓▓▓▒░█▓█░░", "VV¤°¤VV//\\VV¤°¤VV"],
    "megaBoss": [
        "◢▇▆▅▄▃▂ [[[MEGA_BOSS]]] ▂▃▄▅▆▇◣",
        "▓▓<[╦]>▓<<<(¤¤¤)-X-(¤¤¤)>>>▓<[╦]>▓▓",
        "▒▒▒{{{{**@**@**@**}}}}▒▒▒",
        "░░░░\\\\////VVVVVVVV\\\\////░░░░",
        "VVVV----<[코어_파괴]>----VVVV"
    ],
    "missile": ["  ▲  ", " ╱█╲ ", "═╧╧╧═"],
    "multiMissile": ["  ▲   ▲   ▲  ", " ╱█╲ ╱█╲ ╱█╲ ", "═╧╧╧═╧╧╧═╧╧╧═"],
    "bullet": ["•"],
    "explosion": [ # Simplified a bit for Python example, JS has more complex ones
        ["*"],
        [".*."],
        ["-*-"],
        ["\\|/"],
        ["`'.`'"]
    ],
    # particleSystem, hexStructure, spaceStation, planet (from JS, not fully detailed here for brevity but can be added)
    "particleSystem": [["."]],
    "hexStructure": [[" H "]],
    "spaceStation": [["|=|"]],
    "planet": [["(O)"]],
    "banner_waveIncoming": [
        "WW   WW   AA   VV  VV EEEEEEE ",
        "WW   WW  AAAA  VV  VV EE      ",
        "WW W WW AA  AA  VVVV  EEEEEEE ",
        " WWW WWW AAAAAA  VV   EE      ",
        "  WW WW AA  AA  VV   EEEEEEE ",
        "-----------------------------",
        "   I N C O M I N G ! ! !     "
    ],
    "banner_serpentSighted": [
        " SSSSS  EEEEEEE RRRRRR  PPPPPP  EEEEEEE NN   NN TTTTTTT ",
        "SS      EE      RR   RR PP   PP EE      NNN  NN   TTT   ",
        " SSSSS  EEEEEEE RRRRRR  PPPPPP  EEEEEEE NN N NN   TTT   ",
        "     SS EE      RR  RR  PP      EE      NN  NNN   TTT   ",
        " SSSSS  EEEEEEE RR   RR PP      EEEEEEE NN   NN   TTT   "
    ],
    "banner_bossIncoming": [
        "BBBBBB   OOOOO   SSSSS   SSSSS  !! ",
        "BB   BB OO   OO SS      SS      !! ",
        "BBBBBB  OO   OO  SSSSS   SSSSS  !! ",
        "BB   BB OO   OO      SS      SS    ",
        "BBBBBB   OOOOO   SSSSS   SSSSS  !! "
    ]
}

# --- Color Definitions (Map CSS classes to curses color pair IDs) ---
# These will be initialized in AsciiRenderer
COLOR_MAP = {
    'text-default': 1,
    'bullet-orange': 2,
    'laser-white': 3,
    'laser-green': 4,
    'powerup-text': 5,
    'explosion-c1': 6,  # Yellow
    'explosion-c2': 2,  # Orange (using yellow again)
    'explosion-c3': 7,  # Red
    'explosion-c4': 7,  # Red
    'death-symbol-color': 8, # White on Black (dim)
    'hud-name': 6, # Yellow
    'serpent-head': 7, # Red
    'serpent-body': 4, # Green
    'banner-text': 9  # Magenta
}

DEFAULT_COLOR_PAIR = COLOR_MAP['text-default']

# --- Game State ---
class GameState:
    def __init__(self):
        self.reset()

    def reset(self, mode=None):
        self.player = {
            "pos": Vector2(math.floor(GAME_WIDTH / 2), GAME_HEIGHT - 7),
            "currentArt": ASCII_ART["player"][0],
            "artCycle": 0,
            "health": 100,
            "projectiles": [],
            "explosions": [],
            "selectedWeapon": "bullet", # or 'laser'
            "laserCharges": 3,
            "shootCooldown": 0,
            "isLarge": False,
            "sizeIncreaseTimer": 0,
            "activeLasers": [],
            "manualControl": False, # For debug/testing
        }
        self.enemies = []
        self.boss = None
        self.powerUps = []
        self.score = 0
        self.difficulty = 0.5
        self.gameOver = False
        self.tick = 0
        self.hudName = self.generateRandomName()
        self.enemySpawnEvent = None
        self.serpents = []
        self.activeBanners = []
        self.initBackground()

        if mode:
            self.setMode(mode)

    def generateRandomName(self):
        parts = ["Zorp", "Glar", "Fluxx", "Kryll", "Vex", "Nebu", "Xylo", "Quantum", "Hyper", "Void"]
        return random.choice(parts) + str(random.randint(100, 999))

    def initBackground(self):
        self.background = {"layers": [], "planets": [], "detailedElements": []}
        # Simple star layer
        for _ in range(100):
            self.background["layers"].append([{
                "pos": Vector2(random.randint(0, GAME_WIDTH - 1), random.randint(0, GAME_HEIGHT - 1)),
                "char": random.choice(['.', '*', '+']),
                "speed": random.randint(2, 5)
            }])
        # Add a planet
        self.background["planets"].append({
            "pos": Vector2(random.randint(0, GAME_WIDTH-10), -10),
            "char": "O", "innerChar":"o", "size":3, "speed": 0.1
        })


    def setMode(self, modeNumber):
        # print(f"Setting game mode: {modeNumber}") # Can't print directly when curses is active
        self.score = 0
        self.difficulty = 0.5 + (modeNumber - 1) * 0.5
        self.tick = 0
        self.enemies = []
        self.serpents = []
        self.boss = None
        self.powerUps = []
        self.player["activeLasers"] = []
        self.player["projectiles"] = [] # Clear projectiles too
        self.player["pos"] = Vector2(math.floor(GAME_WIDTH / 2), GAME_HEIGHT - 7)
        self.player["health"] = 150 + (modeNumber - 1) * 25
        self.player["laserCharges"] = 1 + math.floor((modeNumber - 1) / 2)
        self.enemySpawnEvent = None
        gameLogic.lastSerpentSpawnTick = -gameLogic.serpentSpawnCooldown # Global gameLogic needed

        # Game over needs to be reset as well
        self.gameOver = False


        # Note: gameLogic methods like spawnBoss, startEnemySpawnEvent, addBanner
        # will be called via the global gameLogic instance.
        if modeNumber == 1:
            self.difficulty = 0.5
        elif modeNumber == 2:
            self.difficulty = 1.0
            self.score = 1500
        elif modeNumber == 3:
            self.difficulty = 1.5
            self.score = 2500
            gameLogic.spawnBoss('regular')
            self.enemySpawnEvent = {'type': 'boss_adds', 'duration': float('inf'), 'spawnInterval': 120, 'ticksUntilNextSpawn': 60, 'initialDelay': 0}
        elif modeNumber == 4:
            self.difficulty = 2.0
            self.score = 4000
            gameLogic.spawnSerpent()
            gameLogic.startEnemySpawnEvent('flood', 240, 3)
            self.addBanner(ASCII_ART["banner_serpentSighted"], "SERPENT SWARM!")
        elif modeNumber == 5:
            self.difficulty = 2.5
            self.score = 6000
            gameLogic.spawnBoss('mega')
            self.enemySpawnEvent = {'type': 'boss_adds', 'duration': float('inf'), 'spawnInterval': 90, 'ticksUntilNextSpawn': 45, 'initialDelay': 0}
        else:
            # print(f"Unknown mode: {modeNumber}")
            pass


    def addBanner(self, art, textFallback=""):
        bannerHeight = len(art)
        bannerWidth = len(art[0]) if bannerHeight > 0 else 0
        self.activeBanners.append({
            "art": art,
            "text": textFallback,
            "pos": Vector2(GAME_WIDTH, math.floor((GAME_HEIGHT - bannerHeight) / 2)),
            "speed": 1,
            "duration": math.floor((GAME_WIDTH + bannerWidth) / 1) + 60,
        })

# --- Renderer ---
class AsciiRenderer:
    def __init__(self, stdscr, gameState):
        self.stdscr = stdscr
        self.gameState = gameState
        self.init_colors()

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors() # Allows using -1 for default terminal bg/fg

        # Pair 0 is default white on black (or terminal default)
        # Pair 1: Cyan on Black (text-default)
        curses.init_pair(COLOR_MAP['text-default'], curses.COLOR_CYAN, curses.COLOR_BLACK)
        # Pair 2: Yellow on Black (bullet-orange, explosion-c2)
        curses.init_pair(COLOR_MAP['bullet-orange'], curses.COLOR_YELLOW, curses.COLOR_BLACK)
        # Pair 3: White on Black (laser-white)
        curses.init_pair(COLOR_MAP['laser-white'], curses.COLOR_WHITE, curses.COLOR_BLACK)
        # Pair 4: Green on Black (laser-green, serpent-body)
        curses.init_pair(COLOR_MAP['laser-green'], curses.COLOR_GREEN, curses.COLOR_BLACK)
        # Pair 5: Bright Green on Black (powerup-text)
        curses.init_pair(COLOR_MAP['powerup-text'], curses.COLOR_GREEN, curses.COLOR_BLACK) # Using normal green, add A_BOLD later
        # Pair 6: Bright Yellow on Black (explosion-c1, hud-name)
        curses.init_pair(COLOR_MAP['explosion-c1'], curses.COLOR_YELLOW, curses.COLOR_BLACK) # Using normal yellow, add A_BOLD later
        # Pair 7: Red on Black (explosion-c3, c4, serpent-head)
        curses.init_pair(COLOR_MAP['explosion-c3'], curses.COLOR_RED, curses.COLOR_BLACK)
        # Pair 8: Dim White on Black (death-symbol) - use normal white, or COLOR_BLACK on COLOR_WHITE if it means gray bg
        curses.init_pair(COLOR_MAP['death-symbol-color'], curses.COLOR_WHITE, curses.COLOR_BLACK) # curses.A_DIM might work too
        # Pair 9: Magenta on Black (banner-text)
        curses.init_pair(COLOR_MAP['banner-text'], curses.COLOR_MAGENTA, curses.COLOR_BLACK)


    def get_color_pair(self, color_name_or_id, char_for_explosion=None):
        if isinstance(color_name_or_id, str):
            if color_name_or_id.startswith('explosion'): # Special handling for explosion multi-colors
                return curses.color_pair(self.get_explosion_color_id(char_for_explosion))
            return curses.color_pair(COLOR_MAP.get(color_name_or_id, DEFAULT_COLOR_PAIR))
        return curses.color_pair(color_name_or_id) # Assume it's already an ID

    def drawArtAtPosition(self, art, pos, color_name_or_id="text-default"):
        if not art: return
        resolved_color_pair = self.get_color_pair(color_name_or_id)

        for dy, line in enumerate(art):
            y = math.floor(pos.y + dy)
            if not (0 <= y < GAME_HEIGHT):
                continue
            for dx, char_to_draw in enumerate(line):
                x = math.floor(pos.x + dx)
                if not (0 <= x < GAME_WIDTH):
                    continue
                if char_to_draw != ' ':
                    # For explosions, we might need char-specific coloring
                    current_pair = resolved_color_pair
                    if isinstance(color_name_or_id, str) and color_name_or_id.startswith('explosion'): # Bit of a hack for explosion
                         current_pair = self.get_color_pair(color_name_or_id, char_to_draw)

                    try:
                        self.stdscr.addch(y, x, char_to_draw, current_pair)
                    except curses.error: # Out of bounds, etc.
                        pass
    
    def drawBackground(self):
        state = self.gameState
        default_pair = self.get_color_pair('text-default')

        for layer_group in state.background["layers"]:
            for element in layer_group:
                if state.tick % element["speed"] == 0:
                    element["pos"].y += 1
                    if element["pos"].y >= GAME_HEIGHT:
                        element["pos"].y = 0
                        element["pos"].x = random.randint(0, GAME_WIDTH - 1)
                
                ey, ex = math.floor(element["pos"].y), math.floor(element["pos"].x)
                if 0 <= ey < GAME_HEIGHT and 0 <= ex < GAME_WIDTH:
                    try:
                        self.stdscr.addch(ey, ex, element["char"], default_pair)
                    except curses.error: pass
        
        for planet in state.background["planets"]:
            if state.tick % math.floor(1 / (planet.get("speed",0.1) or 0.1)) == 0:
                planet["pos"].y += 0.1 # Slow movement
                if planet["pos"].y - planet["size"] >= GAME_HEIGHT:
                    planet["pos"].y = -(planet["size"] * 2 + 1)
                    planet["pos"].x = random.randint(0, GAME_WIDTH - 1)
            
            size = planet["size"]
            for dy_offset in range(-size, size + 1):
                for dx_offset in range(-size, size + 1):
                    if dx_offset*dx_offset + dy_offset*dy_offset <= size*size:
                        px = math.floor(planet["pos"].x + dx_offset)
                        py = math.floor(planet["pos"].y + dy_offset)
                        if 0 <= px < GAME_WIDTH and 0 <= py < GAME_HEIGHT:
                            char_to_draw = planet["innerChar"] if dx_offset*dx_offset + dy_offset*dy_offset <= (size-1)*(size-1) else planet["char"]
                            try:
                                self.stdscr.addch(py, px, char_to_draw, default_pair)
                            except curses.error: pass
        # Detailed elements skipped for brevity but would follow similar logic


    def get_explosion_color_id(self, char): # Returns color pair ID
        # Simplified from JS version for basic curses colors
        if char in '█▓' or (ASCII_ART["explosion"] and len(ASCII_ART["explosion"]) > 4 and ASCII_ART["explosion"][4] and char == ASCII_ART["explosion"][4][0][math.floor(len(ASCII_ART["explosion"][4][0])/2)]):
            return COLOR_MAP['explosion-c1'] # Yellow
        if char in '▒*@' or (ASCII_ART["explosion"] and len(ASCII_ART["explosion"]) > 4 and ASCII_ART["explosion"][4] and char == ASCII_ART["explosion"][4][0][math.floor(len(ASCII_ART["explosion"][4][0])/2)]): # check art
            return COLOR_MAP['explosion-c2'] # Orange (using yellow)
        if char in '░\\|/-=':
            return COLOR_MAP['explosion-c3'] # Red
        return COLOR_MAP['explosion-c4'] # Red

    def drawExplosions(self):
        state = self.gameState
        # Filter and draw explosions
        new_explosions = []
        for explosion in state.player.get("explosions", []): # Use .get for safety
            explosion["frameTick"] += 1
            if explosion["frameTick"] >= explosion["frameSpeed"]:
                explosion["frameTick"] = 0
                explosion["currentFrame"] += 1
            
            if explosion["currentFrame"] < len(explosion["animation"]):
                art = explosion["animation"][explosion["currentFrame"]]
                draw_pos = Vector2(explosion["pos"].x - math.floor(len(art[0]) / 2),
                                   explosion["pos"].y - math.floor(len(art) / 2))
                # This is tricky: drawArtAtPosition expects one color, but explosions use multiple
                # So, we pass a special string 'explosion-dynamic' or similar
                # and let drawArtAtPosition use get_explosion_color_id based on char
                self.drawArtAtPosition(art, draw_pos, "explosion-dynamic") # Special flag
                new_explosions.append(explosion)
        state.player["explosions"] = new_explosions


    def drawLasers(self):
        state = self.gameState
        for laser in state.player.get("activeLasers", []):
            if laser.get("active"):
                laser_pair = self.get_color_pair(laser.get("colorClass", 'laser-white'))
                char_to_draw = laser.get("char", '|')
                for y in range(math.floor(laser["startPos"].y) - 1, -1, -1):
                    if y < GAME_HEIGHT:
                        try:
                            self.stdscr.addch(y, math.floor(laser["startPos"].x), char_to_draw, laser_pair)
                            if laser.get("width", 1) > 1:
                                if laser["startPos"].x - 1 >= 0:
                                    self.stdscr.addch(y, math.floor(laser["startPos"].x - 1), char_to_draw, laser_pair)
                                if laser["startPos"].x + 1 < GAME_WIDTH:
                                    self.stdscr.addch(y, math.floor(laser["startPos"].x + 1), char_to_draw, laser_pair)
                        except curses.error: pass
        
        for enemy in state.enemies:
            if enemy.get("activeLasers"):
                for laser in enemy["activeLasers"]:
                    if laser.get("active"):
                        laser_pair = self.get_color_pair(laser.get("colorClass", 'laser-white')) # Enemy lasers are usually red or distinct
                        char_to_draw = laser.get("char", '|')
                        for y in range(math.floor(laser["startPos"].y) + 1, GAME_HEIGHT):
                             if y >= 0:
                                try:
                                    self.stdscr.addch(y, math.floor(laser["startPos"].x), char_to_draw, laser_pair)
                                except curses.error: pass
        
        if state.boss and state.boss.get("activeLasers"):
            for laser in state.boss["activeLasers"]:
                if laser.get("active"):
                    laser_pair = self.get_color_pair(laser.get("colorClass", 'laser-green'))
                    char_to_draw = laser.get("char", '█')
                    for y in range(math.floor(laser["startPos"].y) + 1, GAME_HEIGHT):
                        if y >= 0 and 0 <= laser["startPos"].x < GAME_WIDTH:
                            try:
                                self.stdscr.addch(y, math.floor(laser["startPos"].x), char_to_draw, laser_pair)
                            except curses.error: pass

    def drawSerpents(self):
        for serpent in self.gameState.serpents:
            body_pair = self.get_color_pair('serpent-body')
            head_pair = self.get_color_pair('serpent-head')
            for i in range(len(serpent["segments"]) - 1, 0, -1):
                self.drawArtAtPosition(ASCII_ART["serpentBody"], serpent["segments"][i]["pos"], 'serpent-body')
            if serpent["segments"]:
                self.drawArtAtPosition(ASCII_ART["serpentHead"], serpent["segments"][0]["pos"], 'serpent-head')
    
    def drawBanners(self):
        banner_pair = self.get_color_pair('banner-text')
        for banner in self.gameState.activeBanners:
            self.drawArtAtPosition(banner["art"], banner["pos"], 'banner-text')


    def render(self):
        self.stdscr.erase() # Clear screen
        state = self.gameState

        if state.gameOver:
            death_art = ASCII_ART["deathSymbol"]
            art_h, art_w = len(death_art), len(death_art[0])
            start_y = (GAME_HEIGHT - art_h) // 2
            start_x = (GAME_WIDTH - art_w) // 2
            self.drawArtAtPosition(death_art, Vector2(start_x, start_y), 'death-symbol-color')
            
            msg = "GAME OVER"
            self.stdscr.addstr(start_y + art_h + 1, (GAME_WIDTH - len(msg)) // 2, msg, self.get_color_pair('text-default'))
            msg2 = f"Score: {state.score}"
            self.stdscr.addstr(start_y + art_h + 2, (GAME_WIDTH - len(msg2)) // 2, msg2, self.get_color_pair('text-default'))
            msg3 = "Press 1-5 to restart in a mode, or Q to quit."
            self.stdscr.addstr(start_y + art_h + 3, (GAME_WIDTH - len(msg3)) // 2, msg3, self.get_color_pair('text-default'))
        else:
            self.drawBackground()
            self.drawArtAtPosition(state.player["currentArt"], state.player["pos"], 'text-default') # Player default color
            
            for enemy in state.enemies:
                self.drawArtAtPosition(enemy.get("art", ASCII_ART["basicEnemy"]), enemy["pos"], 'text-default') # Enemy default color

            self.drawSerpents()

            if state.boss:
                self.drawArtAtPosition(state.boss["art"], state.boss["pos"], 'text-default') # Boss default color
            
            for pu in state.powerUps:
                self.drawArtAtPosition(pu["art"], pu["pos"], 'powerup-text')

            def draw_projectiles_with_art(projectile_list):
                for proj in projectile_list:
                    self.drawArtAtPosition(proj["art"], proj["pos"], 'bullet-orange')
            
            draw_projectiles_with_art(state.player["projectiles"])
            for enemy in state.enemies:
                draw_projectiles_with_art(enemy.get("projectiles", []))
            if state.boss and state.boss.get("projectiles"):
                draw_projectiles_with_art(state.boss["projectiles"])

            self.drawLasers()
            self.drawBanners() # Draw banners over game elements but under explosions
            self.drawExplosions()


        # HUD - Always draw HUD, even on game over for score
        if not state.gameOver : #Only draw full HUD if not game over
            hud_y = GAME_HEIGHT -1 # Draw HUD at the bottom line
            # stat_prefix = random.choice(CHAR_SETS.get("shapes", ["#"])) # CHAR_SETS was empty
            stat_prefix = "#"
            weapon_display = state.player["selectedWeapon"].upper()
            if state.player["selectedWeapon"] == 'laser' and state.player["laserCharges"] == 0:
                weapon_display += " (EMPTY)"
            
            stats_line1 = f"{stat_prefix} {state.hudName} | Score: {state.score} | Health: {state.player['health']}"
            stats_line2 = f"Lasers: {state.player['laserCharges']} | Weapon: {weapon_display}"
            if state.boss:
                stats_line2 += f" | Boss HP: {state.boss['health']}"
            if state.player["isLarge"]:
                stats_line2 += " | SHIP AUGMENTED!"
            if state.player.get("manualControl", False): # Check if key exists
                 stats_line2 += " | MANUAL MODE"
            
            try:
                self.stdscr.addstr(hud_y -1 , 0, stats_line1.ljust(GAME_WIDTH), self.get_color_pair('hud-name'))
                self.stdscr.addstr(hud_y, 0, stats_line2.ljust(GAME_WIDTH), self.get_color_pair('hud-name'))
            except curses.error: pass # Avoid crashing if HUD is too long or off screen
        
        self.stdscr.refresh()

# --- Game Logic ---
class GameLogic:
    def __init__(self, gameState, renderer):
        self.state = gameState
        self.renderer = renderer
        self.explosionFrameSpeed = 3
        self.playerLaserDuration = 25
        self.enemyLaserDuration = 20
        self.megaBossLaserDuration = 45
        self.megaBossMissileCooldown = 120
        self.serpentMoveInterval = 6
        self.serpentRegrowCooldown = 180
        self.serpentShootCooldown = 45
        self.serpentSpawnCooldown = 200
        self.lastSerpentSpawnTick = -self.serpentSpawnCooldown
        self.keys = {} # For held keys, not strictly needed for this game's single press model
        self.gamePaceTargetTime = 7 * 60 * (FPS // 10) # Adjusted for Python ticks (rough estimate)
        # FPS is higher, so target time in ticks needs to be higher

    # setupInputHandlers is implicitly handled by the main loop's getch()
    
    def handle_key_press(self, key_code): # Renamed from handleSingleKeyPress
        player = self.state.player
        
        if self.state.gameOver:
            if key_code in [ord(str(i)) for i in range(1,6)]:
                self.state.reset(int(chr(key_code)))
            elif key_code == ord('q') or key_code == ord('Q'):
                return False # Signal to exit game
            return True

        # Mode switching (can be active anytime for testing)
        if key_code in [ord(str(i)) for i in range(1,6)]:
            self.state.reset(int(chr(key_code)))
            return True

        if key_code == ord('p') or key_code == ord('P'):
            player["manualControl"] = not player.get("manualControl", False) # Use .get
            # Reset movement keys if exiting manual
            if not player["manualControl"]:
                self.keys = {}
            return True

        if player.get("manualControl", False): # Manual control active
            if key_code == ord('a') or key_code == curses.KEY_LEFT: # Left
                player["pos"].x = max(0, player["pos"].x - 2)
            elif key_code == ord('d') or key_code == curses.KEY_RIGHT: # Right
                player["pos"].x = min(GAME_WIDTH - len(player["currentArt"][0]), player["pos"].x + 2)
            elif key_code == ord('w') or key_code == curses.KEY_UP: # Up
                player["pos"].y = max(0, player["pos"].y - 1)
            elif key_code == ord('s') or key_code == curses.KEY_DOWN: # Down
                player["pos"].y = min(GAME_HEIGHT - len(player["currentArt"]), player["pos"].y + 1)
            elif key_code == ord(' '): # Spacebar to shoot
                if player["selectedWeapon"] == "bullet" and player["shootCooldown"] <= 0:
                    art = ASCII_ART["bullet"]
                    player["projectiles"].append({
                        "pos": Vector2(player["pos"].x + math.floor(len(player["currentArt"][0])/2 - len(art[0])/2), player["pos"].y - len(art)),
                        "art": art, "type": "player_bullet"
                    })
                    player["shootCooldown"] = 5 # Cooldown ticks
                elif player["selectedWeapon"] == "laser":
                    self.firePlayerLaser()
            elif key_code == ord('x') or key_code == ord('X'): # Switch weapon
                 player["selectedWeapon"] = "laser" if player["selectedWeapon"] == "bullet" else "bullet"

        elif key_code == ord(' '): # Auto-mode shoot (laser)
            if player["selectedWeapon"] == "laser":
                self.firePlayerLaser()
        elif key_code == ord('x') or key_code == ord('X'): # Switch weapon
            player["selectedWeapon"] = "laser" if player["selectedWeapon"] == "bullet" else "bullet"
        
        return True # Continue game

    def createExplosion(self, position):
        self.state.player["explosions"].append({
            "pos": position,
            "animation": ASCII_ART["explosion"], # Using the simplified one
            "currentFrame": 0,
            "frameTick": 0,
            "frameSpeed": self.explosionFrameSpeed
        })

    def firePlayerLaser(self):
        player = self.state.player
        if player["laserCharges"] > 0 and not any(l.get("active") for l in player.get("activeLasers",[])):
            player["laserCharges"] -= 1
            player["activeLasers"].append({
                "startPos": Vector2(player["pos"].x + math.floor(len(player["currentArt"][0])/2), player["pos"].y),
                "active": True,
                "duration": self.playerLaserDuration,
                "char": '|', "width": 1, "damage": 5, "colorClass": "laser-white"
            })

    def updatePlayer(self):
        player = self.state.player
        
        # Art cycle
        if self.state.tick % 10 == 0:
            player_art_set = ASCII_ART["player_large"] if player["isLarge"] else ASCII_ART["player"]
            player["artCycle"] = (player["artCycle"] + 1) % len(player_art_set)
            player["currentArt"] = player_art_set[player["artCycle"]]

        # Auto-movement if not manual
        if not player.get("manualControl", False):
            # Simple sway
            player["pos"].x += math.sin(self.state.tick * 0.05) * 0.5
            player["pos"].x = max(0, min(player["pos"].x, GAME_WIDTH - len(player["currentArt"][0])))

        # Auto-shoot bullets if not manual
        if not player.get("manualControl", False) and player["selectedWeapon"] == "bullet" and player["shootCooldown"] <= 0:
            art = ASCII_ART["bullet"]
            base_offset = math.floor(len(player["currentArt"][0])/2 - len(art[0])/2)
            
            projectiles_to_add = [{
                "pos": Vector2(player["pos"].x + base_offset, player["pos"].y - len(art)),
                "art": art, "type": "player_bullet"
            }]

            if player["isLarge"]: # Spread shot when large
                 projectiles_to_add.append({
                    "pos": Vector2(player["pos"].x + base_offset - 2, player["pos"].y - len(art) + 1),
                     "art": art, "type": "player_bullet"
                 })
                 projectiles_to_add.append({
                    "pos": Vector2(player["pos"].x + base_offset + 2, player["pos"].y - len(art) + 1),
                     "art": art, "type": "player_bullet"
                 })
            player["projectiles"].extend(projectiles_to_add)
            player["shootCooldown"] = 8 if player["isLarge"] else 12 # Faster shoot rate if large

        if player["shootCooldown"] > 0:
            player["shootCooldown"] -= 1
        
        # Size increase power-up timer
        if player["isLarge"] and player["sizeIncreaseTimer"] > 0:
            player["sizeIncreaseTimer"] -= 1
            if player["sizeIncreaseTimer"] <= 0:
                player["isLarge"] = False
                player["currentArt"] = ASCII_ART["player"][player["artCycle"] % len(ASCII_ART["player"])]


        # Update active lasers
        active_lasers_new = []
        for laser in player.get("activeLasers", []):
            laser["duration"] -=1
            if laser["duration"] > 0:
                laser["active"] = True
                active_lasers_new.append(laser)
            else:
                laser["active"] = False # Ensure it's marked inactive
        player["activeLasers"] = active_lasers_new
        
        # Cap health
        player["health"] = max(0, player["health"])
        if player["health"] <= 0:
            self.state.gameOver = True
            self.createExplosion(Vector2(player["pos"].x + len(player["currentArt"][0])//2, player["pos"].y + len(player["currentArt"])//2))


    def spawnPowerUp(self):
        state = self.state
        if len(state.powerUps) < 2 and random.random() < 0.003 + state.difficulty * 0.001: # Reduced spawn rate
            ptype = random.choice(["sizeIncrease", "laserCharge"])
            art = ASCII_ART[f"powerUp_{ptype}"]
            state.powerUps.append({
                "pos": Vector2(random.randint(0, GAME_WIDTH - len(art[0])), 0),
                "art": art,
                "type": ptype,
                "speed": 0.3 + random.random() * 0.3
            })

    def updatePowerUps(self):
        state = self.state
        player = state.player
        new_powerups = []
        for pu in state.powerUps:
            pu["pos"].y += pu["speed"]
            if pu["pos"].y >= GAME_HEIGHT:
                continue # Off screen

            # Collision with player
            p_art = player["currentArt"]
            pu_art = pu["art"]
            if (pu["pos"].x < player["pos"].x + len(p_art[0]) and
                pu["pos"].x + len(pu_art[0]) > player["pos"].x and
                pu["pos"].y < player["pos"].y + len(p_art) and
                pu["pos"].y + len(pu_art) > player["pos"].y):
                
                if pu["type"] == "sizeIncrease":
                    player["isLarge"] = True
                    player["sizeIncreaseTimer"] = 300 # Ticks duration
                    # Ensure art updates immediately if needed
                    player["currentArt"] = ASCII_ART["player_large"][player["artCycle"] % len(ASCII_ART["player_large"])]

                elif pu["type"] == "laserCharge":
                    player["laserCharges"] = min(player["laserCharges"] + 1, 5) # Max 5 charges
                
                state.score += 50
                # Don't add to new_powerups, it's collected
            else:
                new_powerups.append(pu)
        state.powerUps = new_powerups

    def startEnemySpawnEvent(self, type='flood', duration=120, spawnInterval=5):
        self.state.enemySpawnEvent = {"type": type, "duration": duration, "spawnInterval": spawnInterval, "ticksUntilNextSpawn": 0, "initialDelay": 30}
        if type == 'flood' and not any(b["text"].upper().startswith("WAVE INCOMING") for b in self.state.activeBanners):
            self.state.addBanner(ASCII_ART["banner_waveIncoming"], "WAVE INCOMING!")
            
    def spawnEnemies(self):
        state = self.state

        if state.boss and state.enemySpawnEvent and state.enemySpawnEvent["type"] == 'boss_adds':
            state.enemySpawnEvent["ticksUntilNextSpawn"] -= 1
            if state.enemySpawnEvent["ticksUntilNextSpawn"] <= 0:
                self.spawnSingleEnemy(False, True)
                state.enemySpawnEvent["ticksUntilNextSpawn"] = state.enemySpawnEvent["spawnInterval"]
            return
        if state.boss: return

        # Handle general enemy spawn events
        if state.enemySpawnEvent:
            if state.enemySpawnEvent.get("initialDelay", 0) > 0:
                state.enemySpawnEvent["initialDelay"] -=1
                return # Wait for initial delay

            state.enemySpawnEvent["duration"] -= 1
            state.enemySpawnEvent["ticksUntilNextSpawn"] -= 1

            if state.enemySpawnEvent["ticksUntilNextSpawn"] <= 0:
                num_to_spawn = 1
                if state.enemySpawnEvent["type"] == 'flood': num_to_spawn = random.randint(1,3)
                
                for _ in range(num_to_spawn):
                    self.spawnSingleEnemy(hangMidScreen=(state.enemySpawnEvent["type"] == 'strategic_hang'))
                
                state.enemySpawnEvent["ticksUntilNextSpawn"] = state.enemySpawnEvent["spawnInterval"]
            
            if state.enemySpawnEvent["duration"] <= 0:
                state.enemySpawnEvent = None # Event over
        
        # Regular spawning if no event
        elif random.random() < (0.01 + 0.005 * state.difficulty):
            self.spawnSingleEnemy(hangMidScreen=(random.random() < 0.2 + 0.05 * state.difficulty))


        # Pacing: Trigger Bosses
        time_based_mega_boss_trigger = state.tick > self.gamePaceTargetTime * 0.9 and state.score > 4500
        score_based_mega_boss_trigger = state.score > 6000

        if not state.boss and (time_based_mega_boss_trigger or score_based_mega_boss_trigger) and state.difficulty >= 2.0:
            self.spawnBoss('mega')
            state.enemySpawnEvent = {'type': 'boss_adds', 'duration': float('inf'), 'spawnInterval': 100 - math.floor(state.difficulty * 10), 'ticksUntilNextSpawn': 50, 'initialDelay': 0}
            if not any(b["text"].upper().startswith("MEGA BOSS") for b in state.activeBanners):
                state.addBanner(ASCII_ART["banner_bossIncoming"], "MEGA BOSS ALERT!")

        elif not state.boss and state.score > 2000 and state.difficulty >= 1.0 and state.tick > self.gamePaceTargetTime * 0.4:
            if not state.boss: # Check again
                self.spawnBoss('regular')
                state.enemySpawnEvent = {'type': 'boss_adds', 'duration': float('inf'), 'spawnInterval': 150 - math.floor(state.difficulty * 15), 'ticksUntilNextSpawn': 75, 'initialDelay': 0}
                if not any(b["text"].upper().startswith("BOSS") for b in state.activeBanners):
                    state.addBanner(ASCII_ART["banner_bossIncoming"], "BOSS APPROACHING!")
        
        # Serpent Spawning
        num_serpent_segments = sum(len(s.get("segments", [])) for s in state.serpents)
        if (len(state.serpents) < 1 and num_serpent_segments == 0 and
            state.tick > self.lastSerpentSpawnTick + self.serpentSpawnCooldown and
            random.random() < (0.003 + 0.0015 * state.difficulty) and
            state.score > 700 and not state.boss):
            
            self.spawnSerpent()
            self.lastSerpentSpawnTick = state.tick
            if not any(b["text"].upper().startswith("SERPENT") for b in state.activeBanners):
                state.addBanner(ASCII_ART["banner_serpentSighted"], "SERPENT DETECTED!")

    def spawnSingleEnemy(self, hangMidScreen=False, isBossAdd=False):
        state = self.state
        current_enemy_count = len(state.enemies) + sum(len(s.get("segments", [])) for s in state.serpents)
        max_enemies = 5 if isBossAdd else (12 + state.difficulty * 6)
        
        if current_enemy_count > max_enemies: return

        enemyType = 'basic_add' if isBossAdd else 'basic'
        enemyArt = ASCII_ART["basicEnemy"]
        if not isBossAdd and state.score > 300 and random.random() < 0.35:
            enemyType = 'laser'
            enemyArt = ASCII_ART["laserEnemy"]
        
        start_x = random.randint(0, GAME_WIDTH - len(enemyArt[0]))
        new_enemy = {
            "pos": Vector2(start_x, 1),
            "moveThreshold": max(1, (5 - math.floor(state.difficulty / 2)) if hangMidScreen else (2 if isBossAdd else (3 - math.floor(state.difficulty)))),
            "projectiles": [], "art": enemyArt, "type": enemyType, "activeLasers": [],
            "aiState": 'descending_to_hang' if hangMidScreen else 'descending',
            "hangTargetY": math.floor(GAME_HEIGHT / 3.5 + random.random() * (GAME_HEIGHT / 4)) if hangMidScreen else -1,
            "hangDuration": (75 + random.random() * 60) if hangMidScreen else 0,
            "movementPattern": {"type": 'straight_down', "ticks": 0, "originalX": start_x},
            "shootCooldown": random.randint(30, 60) # Add shoot cooldown
        }
        if hangMidScreen and not isBossAdd:
            new_enemy["movementPattern"]["type"] = 'sine_horizontal' if random.random() < 0.6 else 'pause_shoot'
            new_enemy["movementPattern"]["amplitude"] = random.randint(3, 6) + 3
            new_enemy["movementPattern"]["period"] = random.randint(30, 40) + 40
            new_enemy["movementPattern"]["originalX"] = new_enemy["pos"].x
        
        state.enemies.append(new_enemy)


    def updateEnemies(self):
        state = self.state
        player_pos = state.player["pos"]
        new_enemies = []

        for enemy in state.enemies:
            # Movement
            enemy["movementPattern"]["ticks"] += 1
            move_y = 0
            move_x = 0

            if enemy["aiState"] == 'descending_to_hang':
                move_y = 0.2 + state.difficulty * 0.05 # Slower descent to hang
                if enemy["pos"].y >= enemy["hangTargetY"]:
                    enemy["aiState"] = 'hanging'
                    enemy["pos"].y = enemy["hangTargetY"] # Snap to target
            elif enemy["aiState"] == 'hanging':
                enemy["hangDuration"] -= 1
                if enemy["hangDuration"] <= 0:
                    enemy["aiState"] = 'descending' # Resume normal descent
                
                # Hanging movement patterns
                pat = enemy["movementPattern"]
                if pat["type"] == 'sine_horizontal':
                    offset = pat["amplitude"] * math.sin(2 * math.pi * pat["ticks"] / pat["period"])
                    enemy["pos"].x = pat["originalX"] + offset
                # 'pause_shoot' implies no movement, just shooting logic below
            
            elif enemy["aiState"] == 'descending':
                move_y = 0.3 + state.difficulty * 0.1 # Normal descent speed
                # Basic homing
                if enemy["type"] != 'basic_add': # Adds don't home as much
                    if enemy["pos"].x < player_pos.x: move_x = 0.1
                    elif enemy["pos"].x > player_pos.x: move_x = -0.1
            
            enemy["pos"].y += move_y
            enemy["pos"].x += move_x
            enemy["pos"].x = max(0, min(enemy["pos"].x, GAME_WIDTH - len(enemy["art"][0])))


            if enemy["pos"].y >= GAME_HEIGHT:
                continue # Off screen

            # Shooting
            enemy["shootCooldown"] = enemy.get("shootCooldown", random.randint(40,80)) -1 # ensure exists
            shoot_chance = 0.005 + state.difficulty * 0.003
            if enemy["type"] == 'laser': shoot_chance *= 1.5 # Laser enemies shoot more
            if enemy["aiState"] == 'hanging' and enemy["movementPattern"]["type"] == 'pause_shoot':
                shoot_chance *= 2.0 # Higher chance during pause_shoot

            if enemy["shootCooldown"] <= 0 and random.random() < shoot_chance :
                enemy["shootCooldown"] = random.randint(60,120) - int(state.difficulty * 10) # Reset cooldown
                if enemy["type"] == 'laser' and not enemy.get("activeLasers"): # Only one laser at a time
                    enemy["activeLasers"] = [{ # simplified, single laser
                        "startPos": Vector2(enemy["pos"].x + len(enemy["art"][0])//2, enemy["pos"].y + len(enemy["art"])),
                        "active": True, "duration": self.enemyLaserDuration, "char": '!', "colorClass": "laser-green" # Distinct enemy laser
                    }]
                elif enemy["type"] != 'laser': # Basic enemies shoot bullets
                    bullet_art = ASCII_ART["bullet"]
                    enemy.get("projectiles",[]).append({
                        "pos": Vector2(enemy["pos"].x + len(enemy["art"][0])//2 - len(bullet_art[0])//2, enemy["pos"].y + len(enemy["art"])),
                        "art": bullet_art, "type": "enemy_bullet"
                    })
            
            # Update enemy lasers
            if enemy.get("activeLasers"):
                active_lasers_new = []
                for laser in enemy["activeLasers"]:
                    laser["duration"] -=1
                    if laser["duration"] > 0 :
                        laser["active"] = True
                        active_lasers_new.append(laser)
                    else:
                        laser["active"] = False
                enemy["activeLasers"] = active_lasers_new

            new_enemies.append(enemy)
        state.enemies = new_enemies

    def spawnBoss(self, type='regular'):
        state = self.state
        if state.boss: return

        if type == 'mega':
            art = ASCII_ART["megaBoss"]
            state.boss = {
                "pos": Vector2(math.floor((GAME_WIDTH - len(art[0])) / 2), -len(art)),
                "art": art, "health": math.floor(350 * state.difficulty), "projectiles": [], "activeLasers": [],
                "speed": 0.2, "type": 'mega', "direction": 1, "aiState": 'entering', "targetY": 3,
                "missileCooldown": 0, "laserCooldown": 0, "currentAttackPattern": 'missiles', "attackTimer": 0,
                "cannonPositions": [
                    {"x": 3, "y": 1}, {"x": len(art[0]) - 4, "y": 1}
                ]
            }
        else: # regular
            art = ASCII_ART["boss"]
            state.boss = {
                "pos": Vector2(math.floor((GAME_WIDTH - len(art[0])) / 2), -len(art)),
                "art": art, "health": math.floor(150 * state.difficulty), "projectiles": [], "activeLasers": [],
                "speed": 0.3, "type": 'regular', "direction": 1, "aiState": 'entering', "targetY": 5,
                "attackTimer": 0
            }
        
        # Add banner if not already present
        banner_text_check = type.upper() + " BOSS"
        if not any(b["text"].upper().startswith(banner_text_check) for b in state.activeBanners):
             state.addBanner(ASCII_ART["banner_bossIncoming"], type.upper() + " BOSS APPROACHING!")


    def spawnSerpent(self):
        state = self.state
        num_segments = 5 + math.floor(state.difficulty)
        segment_health = 10 + math.floor(state.difficulty * 5)
        head_pos_x = random.randint(10, GAME_WIDTH - 10)
        
        serpent = {
            "segments": [],
            "moveTick": 0, "shootTick": 0, "regrowTick": 0,
            "initialLength": num_segments, "segmentHealthBase": segment_health,
            "targetPos": Vector2(state.player["pos"].x, state.player["pos"].y - 10) # Target above player
        }
        for i in range(num_segments):
            serpent["segments"].append({
                "pos": Vector2(head_pos_x, -i * (len(ASCII_ART["serpentBody"])) ), # Start offscreen top
                "lastPos": Vector2(head_pos_x, -i * (len(ASCII_ART["serpentBody"])) -1),
                "health": segment_health
            })
        state.serpents.append(serpent)

    def updateSerpents(self):
        state = self.state
        player_center_x = state.player["pos"].x + len(state.player["currentArt"][0]) // 2

        new_serpents = []
        for serpent in state.serpents:
            if not serpent["segments"]:
                continue # Skip if no segments (will be removed)

            serpent["moveTick"] = serpent.get("moveTick",0) + 1
            if serpent["moveTick"] >= self.serpentMoveInterval:
                serpent["moveTick"] = 0
                head = serpent["segments"][0]
                
                # Head targets player's X, maintains Y distance or slowly closes in
                target_x = player_center_x
                target_y = head["pos"].y # Default to current Y unless logic changes it
                
                # Simple chase logic for head
                if head["pos"].x < target_x : head["pos"].x += 0.5 + 0.1 * state.difficulty
                elif head["pos"].x > target_x: head["pos"].x -= 0.5 + 0.1 * state.difficulty
                
                # Try to maintain some vertical distance or slowly descend
                if head["pos"].y < 5: head["pos"].y += 0.2 # Descend if too high
                elif head["pos"].y < state.player["pos"].y - 15 : head["pos"].y += 0.1 # Slowly close vertical gap

                # Clamp head position
                head["pos"].x = max(0, min(head["pos"].x, GAME_WIDTH - len(ASCII_ART["serpentHead"][0])))
                head["pos"].y = max(0, min(head["pos"].y, GAME_HEIGHT - len(ASCII_ART["serpentHead"])))


                # Body segments follow
                prev_pos = Vector2(head["pos"].x, head["pos"].y) # Store current head to become lastPos
                head["lastPos"] = prev_pos

                for i in range(1, len(serpent["segments"])):
                    segment = serpent["segments"][i]
                    leader = serpent["segments"][i-1]
                    
                    # Store current pos before moving
                    current_segment_pos_copy = Vector2(segment["pos"].x, segment["pos"].y)

                    # Move towards leader's last known position (where leader WAS)
                    dx = leader["lastPos"].x - segment["pos"].x
                    dy = leader["lastPos"].y - segment["pos"].y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    # Ideal distance between segments (approx height of body art)
                    ideal_dist = len(ASCII_ART["serpentBody"]) -1 
                    
                    if dist > ideal_dist : # Only move if too far
                        segment["pos"].x += (dx / dist) * (dist - ideal_dist) * 0.8 # Move a bit to catch up
                        segment["pos"].y += (dy / dist) * (dist - ideal_dist) * 0.8
                    
                    segment["lastPos"] = current_segment_pos_copy


            # Serpent Regrowth
            serpent["regrowTick"] = serpent.get("regrowTick", 0) + 1
            if len(serpent["segments"]) < serpent["initialLength"] and serpent["regrowTick"] >= self.serpentRegrowCooldown:
                if serpent["segments"]: # Can only regrow if there's a tail
                    tail = serpent["segments"][-1]
                    serpent["segments"].append({
                        "pos": Vector2(tail["lastPos"].x, tail["lastPos"].y),
                        "lastPos": Vector2(tail["lastPos"].x, tail["lastPos"].y),
                        "health": serpent["segmentHealthBase"] + math.floor(state.difficulty * 2)
                    })
                serpent["regrowTick"] = 0

            # Serpent Shooting
            serpent["shootTick"] = serpent.get("shootTick",0) + 1
            if serpent["shootTick"] >= self.serpentShootCooldown and serpent["segments"]:
                head = serpent["segments"][0]
                # To put serpent shots into the main enemy projectile system:
                # Create a dummy enemy or just add directly to a global list if easier.
                # For simplicity, we'll add to a generic enemy list for now, which might be confusing.
                # A better way would be a global projectile list.
                # Let's assume self.state.enemies[0] exists and use its projectile list
                # THIS IS A HACK: Create a temporary structure for serpent projectiles
                # that gameLogic.updateProjectiles can handle.
                # A proper solution would be a global projectile list or serpent having its own.
                if state.enemies: # Hack: add to first enemy's projectiles
                     state.enemies[0].get("projectiles",[]).append({
                        "pos": Vector2(head["pos"].x + math.floor(len(ASCII_ART["serpentHead"][0])/2), 
                                       head["pos"].y + len(ASCII_ART["serpentHead"])),
                        "art": ASCII_ART["bullet"], "type": 'enemy_serpent_shot'
                    })
                serpent["shootTick"] = 0
            
            if serpent["segments"]: # Only keep if it has segments
                new_serpents.append(serpent)
        state.serpents = new_serpents


    def updateBoss(self):
        state = self.state
        if not state.boss: return
        boss = state.boss

        if boss["aiState"] == 'entering':
            boss["pos"].y += boss["speed"]
            if boss["pos"].y >= boss["targetY"]:
                boss["aiState"] = 'fighting'
            return

        # Horizontal Movement
        if state.tick % math.floor(5 / boss["speed"]) == 0:
            boss["pos"].x += boss["direction"] * 0.5
        if boss["pos"].x <= 0 or boss["pos"].x + len(boss["art"][0]) >= GAME_WIDTH:
            boss["direction"] *= -1
            boss["pos"].x = max(0, min(boss["pos"].x, GAME_WIDTH - len(boss["art"][0]))) # Clamp


        boss["attackTimer"] = boss.get("attackTimer", 0) + 1

        if boss["type"] == 'mega':
            boss["missileCooldown"] = max(0, boss.get("missileCooldown",0) - 1)
            boss["laserCooldown"] = max(0, boss.get("laserCooldown",0) - 1)

            if boss["attackTimer"] > 180: # Approx 3 seconds at 60 FPS equivalent
                boss["currentAttackPattern"] = 'missiles' if random.random() < 0.6 else 'laser_sweep'
                boss["attackTimer"] = 0
            
            if boss["currentAttackPattern"] == 'missiles' and boss["missileCooldown"] == 0:
                for cannon in boss.get("cannonPositions",[]):
                    missile_type_art = ASCII_ART["multiMissile"] if random.random() < 0.3 else ASCII_ART["missile"]
                    spawn_x_offset = math.floor(len(missile_type_art[0]) / (6 if missile_type_art == ASCII_ART["multiMissile"] else 2)) * (1 if random.random() > 0.5 else -1)
                    spawn_x = boss["pos"].x + cannon["x"] + spawn_x_offset
                    
                    boss.get("projectiles",[]).append({
                        "pos": Vector2(spawn_x, boss["pos"].y + cannon["y"] + len(missile_type_art) -1),
                        "art": missile_type_art, "type": 'boss_missile', "speedY": 0.4 + random.random()*0.2 # Python version might need slower speeds
                    })
                boss["missileCooldown"] = 90 + random.randint(0,60) - state.difficulty * 10
            
            elif boss["currentAttackPattern"] == 'laser_sweep' and boss["laserCooldown"] == 0 and not boss.get("activeLasers"):
                laser_x = boss["pos"].x + math.floor(len(boss["art"][0]) / 2)
                boss["activeLasers"] = [{ # List of lasers
                    "startPos": Vector2(laser_x, boss["pos"].y + len(boss["art"]) - 1),
                    "active": True, "duration": self.megaBossLaserDuration,
                    "char": '█', "width": 3, "damage": 1.5, "colorClass": 'laser-green',
                    "sweepSpeed": 0.1 * (1 if random.random() < 0.5 else -1), # Slower sweep for terminal
                    "sweepMaxOffset": 10 # Smaller offset
                }]
                boss["laserCooldown"] = 150 - state.difficulty * 15
        
        else: # Regular boss
            if boss["attackTimer"] > (120 - state.difficulty * 10):
                spread = math.floor(state.difficulty)
                for i in range(-spread, spread + 1):
                    boss.get("projectiles",[]).append({
                        "pos": Vector2(boss["pos"].x + math.floor(len(boss["art"][0])/2) + i*3, boss["pos"].y + len(boss["art"])),
                        "art": ASCII_ART["bullet"], "type": 'boss_bullet' # Renamed from 'boss'
                    })
                boss["attackTimer"] = 0

        # Update boss lasers (sweep)
        if boss.get("activeLasers"):
            new_active_lasers = []
            for laser in boss["activeLasers"]:
                laser["duration"] -= 1
                if laser.get("sweepSpeed"):
                    laser["startPos"].x += laser["sweepSpeed"]
                    center_x = boss["pos"].x + math.floor(len(boss["art"][0]) / 2)
                    if abs(laser["startPos"].x - center_x) > laser.get("sweepMaxOffset",15):
                        laser["sweepSpeed"] *= -1
                        laser["startPos"].x = center_x + math.copysign(laser["sweepMaxOffset"], laser["startPos"].x - center_x)
                
                if laser["duration"] > 0:
                    laser["active"] = True
                    new_active_lasers.append(laser)
                else:
                    laser["active"] = False # Explicitly set to false
            boss["activeLasers"] = new_active_lasers


    def updateProjectiles(self):
        state = self.state
        player = state.player

        # Update player projectiles
        new_player_projectiles = []
        for proj in player["projectiles"]:
            proj["pos"].y -= 1.5 # Player bullets faster
            if proj["pos"].y < -len(proj["art"]): # Check off-screen top
                continue
            
            collided = False
            # Check collision with basic enemies
            for enemy in state.enemies[:]: # Iterate copy for removal
                e_art = enemy["art"]
                if (proj["pos"].x < enemy["pos"].x + len(e_art[0]) and
                    proj["pos"].x + len(proj["art"][0]) > enemy["pos"].x and
                    proj["pos"].y < enemy["pos"].y + len(e_art) and
                    proj["pos"].y + len(proj["art"]) > enemy["pos"].y):
                    # Enemy hit
                    self.createExplosion(Vector2(proj["pos"].x + len(proj["art"][0])//2, proj["pos"].y))
                    state.enemies.remove(enemy)
                    state.score += 10
                    collided = True
                    break 
            if collided: continue

            # Check collision with serpent segments
            for serpent in state.serpents:
                for segment in serpent["segments"][:]: # Iterate copy
                    s_art = ASCII_ART["serpentHead"] if segment == serpent["segments"][0] else ASCII_ART["serpentBody"]
                    if (proj["pos"].x < segment["pos"].x + len(s_art[0]) and
                        proj["pos"].x + len(proj["art"][0]) > segment["pos"].x and
                        proj["pos"].y < segment["pos"].y + len(s_art) and
                        proj["pos"].y + len(proj["art"]) > segment["pos"].y):
                        
                        segment["health"] = segment.get("health", 10) - 10 # Damage
                        self.createExplosion(Vector2(proj["pos"].x + len(proj["art"][0])//2, proj["pos"].y))
                        if segment["health"] <= 0:
                            serpent["segments"].remove(segment)
                            state.score += 25
                        collided = True
                        break
                if collided: break
            if collided: continue
            
            # Check collision with Boss
            if state.boss:
                b_art = state.boss["art"]
                if (proj["pos"].x < state.boss["pos"].x + len(b_art[0]) and
                    proj["pos"].x + len(proj["art"][0]) > state.boss["pos"].x and
                    proj["pos"].y < state.boss["pos"].y + len(b_art) and
                    proj["pos"].y + len(proj["art"]) > state.boss["pos"].y):
                    
                    state.boss["health"] -= 10 # Boss damage
                    self.createExplosion(Vector2(proj["pos"].x + len(proj["art"][0])//2, proj["pos"].y))
                    state.score += 5
                    if state.boss["health"] <= 0:
                        self.createExplosion(Vector2(state.boss["pos"].x + len(b_art[0])//2, state.boss["pos"].y + len(b_art)//2)) # Big boom
                        state.score += 500 if state.boss["type"] == 'regular' else 1000
                        state.boss = None # Boss defeated
                        state.enemySpawnEvent = None # Clear boss adds event
                    collided = True
            if collided: continue

            new_player_projectiles.append(proj)
        player["projectiles"] = new_player_projectiles


        # Update enemy/boss projectiles
        def update_non_player_projectiles(projectile_owner_list, is_boss_list=False):
            for owner_idx, owner in enumerate(projectile_owner_list[:]): # Iterate over a copy for safe removal
                if not hasattr(owner, 'get') or not callable(owner.get): # Ensure owner is a dict-like object
                    if is_boss_list: # If it's the boss (single item list)
                        if owner_idx == 0 and state.boss: owner = state.boss
                        else: continue
                    else: # If it's from enemies list
                        if owner_idx < len(state.enemies): owner = state.enemies[owner_idx]
                        else: continue
                
                new_owner_projectiles = []
                for proj in owner.get("projectiles", []):
                    speed_y_multiplier = 1.0
                    if proj["type"] == 'boss_missile':
                        proj["pos"].y += proj.get("speedY", 0.5) # Missile custom speed
                        # Simple homing for missiles
                        player_center_x = player["pos"].x + len(player["currentArt"][0]) / 2
                        if proj["pos"].x < player_center_x and proj["pos"].x < GAME_WIDTH - len(proj["art"][0]): proj["pos"].x += 0.1
                        elif proj["pos"].x > player_center_x and proj["pos"].x > 0: proj["pos"].x -= 0.1
                    else: # Normal bullets
                        speed_y_multiplier = 1.2 if proj["type"] in ['boss_special', 'enemy_serpent_shot'] else 0.7 # Slower enemy bullets
                        proj["pos"].y += speed_y_multiplier
                    
                    if proj["pos"].y >= GAME_HEIGHT or proj["pos"].y < -len(proj["art"]):
                        continue # Off screen

                    # Collision with player
                    p_art = player["currentArt"]
                    if (proj["pos"].x + len(proj["art"][0]) > player["pos"].x and
                        proj["pos"].x < player["pos"].x + len(p_art[0]) and
                        proj["pos"].y + len(proj["art"]) > player["pos"].y and
                        proj["pos"].y < player["pos"].y + len(p_art)):
                        
                        damage = 10
                        if proj["type"] == 'boss_missile': damage = 20
                        elif proj["type"] == 'boss_special': damage = 15 # Assuming 'boss_bullet' is special
                        elif proj["type"] == 'enemy_serpent_shot': damage = 12
                        
                        player["health"] -= damage
                        self.createExplosion(Vector2(proj["pos"].x + len(proj["art"][0])//2, proj["pos"].y + len(proj["art"])//2))
                        if player["health"] <= 0:
                            player["health"] = 0
                            state.gameOver = True
                        # Projectile is consumed
                    else:
                        new_owner_projectiles.append(proj)
                
                # Update the owner's projectile list
                if is_boss_list:
                    if state.boss: state.boss["projectiles"] = new_owner_projectiles
                else:
                    if owner_idx < len(state.enemies): # Check if enemy still exists
                         state.enemies[owner_idx]["projectiles"] = new_owner_projectiles
        
        update_non_player_projectiles(state.enemies)
        if state.boss:
            update_non_player_projectiles([state.boss], is_boss_list=True) # Pass boss as a list


    def checkLaserCollisions(self): # Simplified
        state = self.state
        player = state.player

        # Player laser hitting things
        for laser in player.get("activeLasers", []):
            if not laser.get("active"): continue
            laser_x = math.floor(laser["startPos"].x)
            laser_damage = laser.get("damage",1)

            # Player laser vs enemies
            for enemy in state.enemies[:]:
                e_art_width = len(enemy["art"][0])
                if (enemy["pos"].x <= laser_x < enemy["pos"].x + e_art_width and
                    enemy["pos"].y + len(enemy["art"]) > 0): # Enemy is below laser start, in its path
                    # Continuous damage
                    self.createExplosion(Vector2(laser_x, enemy["pos"].y + len(enemy["art"])//2)) # Small sparks
                    # For simplicity, let's say laser insta-kills basic enemies
                    state.enemies.remove(enemy)
                    state.score += 15
            
            # Player laser vs serpent segments
            for serpent in state.serpents:
                 for segment in serpent["segments"][:]:
                    s_art = ASCII_ART["serpentHead"] if segment == serpent["segments"][0] else ASCII_ART["serpentBody"]
                    s_art_width = len(s_art[0])
                    if (segment["pos"].x <= laser_x < segment["pos"].x + s_art_width and
                        segment["pos"].y + len(s_art) > 0):
                        segment["health"] = segment.get("health",10) - laser_damage # Continuous damage
                        self.createExplosion(Vector2(laser_x, segment["pos"].y + len(s_art)//2))
                        if segment["health"] <= 0:
                            serpent["segments"].remove(segment)
                            state.score += 30
            
            # Player laser vs Boss
            if state.boss:
                b_art_width = len(state.boss["art"][0])
                if (state.boss["pos"].x <= laser_x < state.boss["pos"].x + b_art_width and
                    state.boss["pos"].y + len(state.boss["art"]) > 0):
                    state.boss["health"] -= laser_damage
                    state.score += int(laser_damage / 2) # Score for damage
                    self.createExplosion(Vector2(laser_x, state.boss["pos"].y + len(state.boss["art"])//2))
                    if state.boss["health"] <= 0:
                        self.createExplosion(Vector2(state.boss["pos"].x + b_art_width//2, state.boss["pos"].y + len(state.boss["art"])//2))
                        state.score += 500 if state.boss["type"] == 'regular' else 1000
                        state.boss = None
                        state.enemySpawnEvent = None


        # Enemy/Boss lasers hitting player
        lasers_to_check = []
        for enemy in state.enemies: lasers_to_check.extend(enemy.get("activeLasers",[]))
        if state.boss: lasers_to_check.extend(state.boss.get("activeLasers",[]))

        for laser in lasers_to_check:
            if not laser.get("active"): continue
            laser_x = math.floor(laser["startPos"].x)
            p_art_width = len(player["currentArt"][0])
            if (player["pos"].x <= laser_x < player["pos"].x + p_art_width and
                player["pos"].y < laser["startPos"].y): # Player is above laser start, in its path
                player["health"] -= laser.get("damage", 1) # Enemy laser damage
                # Small explosion on player
                self.createExplosion(Vector2(laser_x, player["pos"].y + len(player["currentArt"])//2))
                if player["health"] <= 0:
                    state.gameOver = True
                    break # Player destroyed


    def checkCollisions(self): # Player ship vs enemy ship
        state = self.state
        player = state.player
        if state.gameOver: return

        p_x, p_y = player["pos"].x, player["pos"].y
        p_w, p_h = len(player["currentArt"][0]), len(player["currentArt"])

        # Player vs Enemies
        for enemy in state.enemies[:]:
            e_x, e_y = enemy["pos"].x, enemy["pos"].y
            e_w, e_h = len(enemy["art"][0]), len(enemy["art"])
            if (p_x < e_x + e_w and p_x + p_w > e_x and
                p_y < e_y + e_h and p_y + p_h > e_y):
                player["health"] -= 25 # Collision damage
                self.createExplosion(Vector2( (p_x+p_w/2 + e_x+e_w/2)/2, (p_y+p_h/2 + e_y+e_h/2)/2 ))
                state.enemies.remove(enemy) # Enemy destroyed by collision
                state.score += 5
                if player["health"] <= 0: state.gameOver = True; return

        # Player vs Serpent Segments
        for serpent in state.serpents:
            for segment in serpent["segments"][:]:
                s_art = ASCII_ART["serpentHead"] if segment == serpent["segments"][0] else ASCII_ART["serpentBody"]
                s_x, s_y = segment["pos"].x, segment["pos"].y
                s_w, s_h = len(s_art[0]), len(s_art)
                if (p_x < s_x + s_w and p_x + p_w > s_x and
                    p_y < s_y + s_h and p_y + p_h > s_y):
                    player["health"] -= 30
                    segment["health"] = segment.get("health",10) - 50 # Segment takes massive damage
                    self.createExplosion(Vector2( (p_x+p_w/2 + s_x+s_w/2)/2, (p_y+p_h/2 + s_y+s_h/2)/2 ))
                    if segment["health"] <= 0:
                        serpent["segments"].remove(segment)
                        state.score += 10
                    if player["health"] <= 0: state.gameOver = True; return
        
        # Player vs Boss (less likely due to boss size/position, but possible)
        if state.boss:
            b_x, b_y = state.boss["pos"].x, state.boss["pos"].y
            b_w, b_h = len(state.boss["art"][0]), len(state.boss["art"])
            if (p_x < b_x + b_w and p_x + p_w > b_x and
                p_y < b_y + b_h and p_y + p_h > b_y):
                player["health"] -= 50 # Major collision damage
                state.boss["health"] -= 50 # Boss also takes damage
                self.createExplosion(Vector2( (p_x+p_w/2 + b_x+b_w/2)/2, (p_y+p_h/2 + b_y+b_h/2)/2 ))
                if state.boss["health"] <= 0: state.boss = None; state.score += 200
                if player["health"] <= 0: state.gameOver = True; return

    def updateBanners(self):
        state = self.state
        new_banners = []
        for banner in state.activeBanners:
            banner["pos"].x -= banner["speed"]
            banner["duration"] -= 1
            if banner["duration"] > 0:
                new_banners.append(banner)
        state.activeBanners = new_banners

    def gameLoop(self, stdscr):
        global gameLogic # Allow setMode to access the global gameLogic instance

        stdscr.nodelay(True) # Non-blocking input
        stdscr.timeout(0) # Make getch non-blocking immediately (alternative to nodelay for some cases)
        curses.curs_set(0) # Hide cursor

        game_running = True
        while game_running:
            input_key = stdscr.getch()
            if input_key != -1:
                if not self.handle_key_press(input_key):
                    game_running = False # Exit signal from handle_key_press
                    break

            if not self.state.gameOver:
                self.state.tick += 1
                self.updatePlayer()
                self.spawnPowerUp()
                self.updatePowerUps()
                self.spawnEnemies()
                self.updateEnemies()
                self.updateSerpents() # Must be before updateBoss if serpents can be boss adds
                self.updateBoss()
                self.updateProjectiles()
                self.checkLaserCollisions() # Check before general collisions
                self.checkCollisions()
                self.updateBanners()

                # Difficulty scaling
                difficulty_cap = 3.5
                target_difficulty_time = 0.5 + (self.state.tick / (self.gamePaceTargetTime / (difficulty_cap - 0.5)))
                target_difficulty_score = 0.5 + math.floor(self.state.score / 1500) * 0.5
                
                target_difficulty = max(target_difficulty_time, target_difficulty_score)
                target_difficulty = min(difficulty_cap, target_difficulty)

                if target_difficulty > self.state.difficulty:
                    self.state.difficulty = target_difficulty
            
            self.renderer.render()
            
            time.sleep(1 / FPS)
    
    def start(self, stdscr): # stdscr is passed by curses.wrapper
        # Initialize renderer here because stdscr is now available
        self.renderer = AsciiRenderer(stdscr, self.state)
        self.state.setMode(1) # Start in mode 1 by default
        self.gameLoop(stdscr)

# --- Initialize (Global instances) ---
gameState = GameState()
# Renderer is initialized in gameLogic.start once stdscr is available
# gameLogic needs gameState, but renderer is also set up inside its start method.
gameLogic = GameLogic(gameState, None) # Renderer will be set later

def main(stdscr):
    # Pass stdscr to gameLogic to initialize renderer and start game
    gameLogic.start(stdscr)

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except curses.error as e:
        print(f"Curses error: {e}")
        print("Your terminal might be too small or not support colors well.")
        print(f"Required: {GAME_WIDTH}x{GAME_HEIGHT} characters.")
    except Exception as e:
        # Make sure terminal is reset if something else goes wrong
        curses.endwin()
        import traceback
        traceback.print_exc()
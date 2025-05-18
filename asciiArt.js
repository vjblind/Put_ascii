// asciiArt.js

console.log("asciiArt.js loaded.");

// Define the global ASCII_ART object with ALL the art
window.ASCII_ART = {
    player: [ "   ▲   ", "  <█>  ", " ◢◤█◥◣ ", "╿ ▲▲▲ ╿" ],
    player_large: [ "   ▲▲  ", "  <██>  ", " ◢◤▀▀◥◣ ", "╿█ ▲▲ █╿", "  ╲ II ╱  " ],
    player_augmented: [ "  ║ ▲ ║  ", " <╱█╲> ", "◢◣ ▼ ◢◣", "╿█▀▀▀█╿", "  ╲███╱  " ],
    player_avatar: [ "  ^-^  ", " ( o ) ", "  `ӊ`  " ],

    powerUp_sizeIncrease: [ "╭───╮", "│ S │", "╰───╯" ],
    powerUp_laserCharge: [ "╭───╮", "│ L │", "╰───╯" ],
    powerUp_shieldCharge: [ "╭───╮", "│ 🛡 │", "╰───╯" ],
    powerUp_augment: [ "╭───╮", "│ ★ │", "╰───╯" ],

    basicEnemy: [ " ▼▼▼ ", "◢■■■◣", "◥ ▲▲ ◤" ],
    basicEnemy_avatar: [ "  vVv  ", " (oVo) ", "  `ӊ`  " ],

    laserEnemy: [ " <◊═◊> ", "╔═╩█╩═╗", "  ╿╿╿  " ],
    laserEnemy_scout: [ " <◊> ", "╔═█═╗", "  ╿  " ],
    laserEnemy_heavy: ["«<[◊Ξ◊]>»","╠══╦█╦══╣","  ▌╿╿╿▐  ","   ╚═╝   "],
    laserEnemy_avatar: [ "  <->  ", " ( ◊ ) ", "  `ӊ`  " ],

    serpentHead: [ "  .--.  ", " /ö_ö\\ \\ ", " \\ vv / ", "  `~~'  "],
    serpentBody: [ "╭ 形 ╮", "╞═══╡", "╰────╯"],
    serpent_avatar: [ "  .--. ", " /oo\\ \\", " \\__/` " ],
    // New art for mechanical serpent laser projectile
    serpentLaserProjectile: [ "  │  ", "  │  ", "  ▼  " ], // Simple vertical laser

    deathSymbol: [ "   ╔═══╗   ", "   ║RIP║   ", "   ║   ║   ", "╔══╩═══╩══╗", "║          ║", "╚══════════╝" ],

    boss: [ "   ║   ║   ", "^-═<[█]>═-^", "▓▓<[╦]>▓▓", "░░█▓█▓█░░", " VV¤°¤VV " ],
    boss_avatar: [ " <███> ", "[XXXXX]", " VVVVV " ],

    // User provided Titan Boss art
    titanMegaBoss: [
        "      ╔════════◢█████◣════════╗      ",
        "    ◢█<◢▓▓▓<{{{[TITAN]}}}▓▓▓◣>█◣    ",
        "   ◢██╣<[╬╬]>████████████<[╬╬]>╣██◣   ",
        "  ◢███╦════◥<▓▓▓[█]▓▓▓>◤════╦███◣  ",
        " █████╣<◢◣>█████[█]█████<◢◣>╣█████ ",
        "◢█████╬╬╬╬╬◥◤<<<(¤¤¤)>>>◥◤╬╬╬╬╬█████◣",
        "██████╣╣===={{{{**@**@**@**}}}}===╣╣██████",
        "◥█████╩╩---◢◤\\\\////▼▼▼▼\\\\////◥◤---╩╩█████◤",
        " ◥████/|||||\\░<[═══]>░/|||||\████◤ ",
        "  ◥███{||V||}---OVERLORD---{||V||}███◤  ",
        "   ◥██╝VVVVV<<<|>█<|>█<|>>>>VVVVV╚██◤   ",
        "    ◥█<◥▓▓▓<{[DESTROYER]}▓▓▓◤>█◤    ",
        "      ╚════════◥█████◤════════╝      "
    ],
    // User provided Titan Mega Boss avatar
    titanMegaBoss_avatar: [
        " ╔{O}╗ ",
        "<|█▼█|>",
        " VVVVV "
    ],


    missile: [ "  ▼  ", " ╲█╱ ", "═╦╦╦═" ],
    multiMissile: [ "  ▼   ▼   ▼  ", "  ╲█╱ ╲█╱ ╲█╱ ", "═╦╤═╤╤╤╤═╤╤╦═" ],
    bullet: ["•"], // Added back the bullet art

    // Explosions - kept for drawing logic
    explosion: [
        ["   *   ","  * *  ","   *   "],
        ["  \\|/  "," --*-- ","  /|\\  "],
        [" \\\\|// ","-=*@*=-"," //|\\\\ "],
        ["\\\\\\|///","==*@@*==","///|\\\\\\"], // Slightly adjusted 4th frame for '@'
        [" ░▒▓█▓▒░ ","░▒▓███▓▒░","▒▓█████▓▒","▓███████▓","▒▓█████▓▒","░▒▓███▓▒░"," ░▒▓█▓▒░ "] // Large explosion
    ],

    // Hex Structure - kept for shield animation
    hexStructure: [
        ["   ╲   ╱   "," ╭───⛶───╮ "," │╲  *  ╱│ "," ⛶───◊───⛶ "," │╱     ╲│ "," ╰───⛶───╯ ","   ╱   ╲   "],
        ["    ╲ ╱    ","  ╲─────╱  "," ╭─╲ * ╱─╮ "," │   ◊   │ "," ╰─╱   ╲─╯ ","  ╱─────╲  ","    ╱ ╲    "],
        ["   ╱   ╲   "," ╭───◇───╮ "," │╱  ¤  ╲│ "," ◇───*───◇ "," │╲     ╱│ "," ╰───◇───╯ ","   ╲   ╱   "]
    ],

    // Space Station - kept for background art
    spaceStation: [
        "    ╭──────────╮    ",
        "╭───┤ ▓▓▓▓▓▓▓▓ ├───╮",
        "│╭──┤ ▒▒▒▒▒▒▒▒ ├──╮│",
        "││  │ ░░░░░░░░ │  ││",
        "││╭─┤ ▓▓▓▓▓▓▓▓ ├─╮││",
        "│││ └──────────┘ │││",
        "╰╯╰───────────────╯╰╯"
    ],

    // Planet - kept for background art
    planet_saturn_jgs: [
        "         ,MMM8&&&.",
        "    _...MMMMM88&&&&..._",
        " .::'''MMMMM88&&&&&&'''::.",
        "::     MMMMM88&&&&&&     ::",
        "'::....MMMMM88&&&&&&....::'",
        "   `''''MMMMM88&&&&''''`",
        "   jgs   'MMM8&&&'"
    ],

    // Banners - kept for messages
    banner_waveIncoming: [ "WW   WW   AA   VV  VV EEEEEEE ", "WW   WW  AAAA  VV  VV EE      ", "WW W WW AA  AA  VVVV  EEEEEEE ", " WWW WWW AAAAAA  VV   EE      ", "  WW WW AA  AA  VV   EEEEEEE ", "-----------------------------", "   I N C O M I N G ! ! !     " ],
    banner_serpentSighted: [ " SSSSS  EEEEEEE RRRRRR  PPPPPP  EEEEEEE NN   NN TTTTTTT ", "SS      EE      RR   RR PP   PP EE      NNN  NN   TTT   ", " SSSSS  EEEEEEE RRRRRR  PPPPPP  EEEEEEE NN N NN   TTT   ", "     SS EE      RR  RR  PP      EE      NN  NNN   TTT   ", " SSSSS  EEEEEEE RR   RR PP      EEEEEEE NN   NN   TTT   " ],
    banner_bossIncoming: [ "BBBBBB   OOOOO   SSSSS   SSSSS  !! ", "BB   BB OO   OO SS      SS      !! ", "BBBBBB  OO   OO  SSSSS   SSSSS  !! ", "BB   BB OO   OO      SS      SS    ", "BBBBBB   OOOOO   SSSSS   SSSSS  !! " ],
    banner_systemOverride: [ " SSS Y  Y SSS TTT EEEEE M   M ", "S    Y  Y S    T  EE    MM MM ", " SSS  YY   SSS  T  EEEEE M M M ", "    S  Y      S  T  EE    M   M ", " SSS   Y   SSS   T  EEEEE M   M ", "-------------------------------", "   O V E R R I D E : B L U E   " ],
    banner_shipAugmented: [ " SSS H  H III PPPPP     AA   U  U  GGGG M   M EEEEE NNN  NN TTTTT EEEEE DDDDD  ", "S    H  H  I  PP  PP   AAAA  U  U GG     MM MM EE    NNN  NN  TTT  EE    DD  DD ", " SSS HHHH  I  PPPPP   AA  AA U  U GG GGG M M M EEEEE NN N NN  TTT  EEEEE DD  DD ", "    S H  H  I  PP      AAAAAA U  U GG  GG M   M EE    NN  NNN  TTT  EE    DD  DD ", " SSS  H  H III PP       AA  AA UU UU  GGGG M   M EEEEE NN   NN  TTT  EEEEE DDDDD  "],
    // New banner for Mechanical Serpents
    banner_serpentMechanical: [ "MM   MM EEEEEEE  CCCCCC H  H AA   NN   NN III  CCCCCC AA   LL    ", "MMM MMM EE      CC      H  H AAAA NN N NN  I  CC      AAAA  LL    ", "MM M MM EEEEEEE CC      HHHH AA  AA NN  NNN I  CC      AA  AA LL    ", "MM   MM EE      CC      H  H AAAAAA NN  NNN I  CC      AAAAAA LL    ", "MM   MM EEEEEEE  CCCCCC H  H AA  AA NN   NN III  CCCCCC AA  AA LLLLL ", "-----------------------------------------------------------------", "      S E R P E N T   S Y N T H E S I S   D E T E C T E D !      " ]
};

// Add the new art to the existing window.ASCII_ART object
// This way, if you had other external art files, they could potentially
// add to this object as well, as long as this one loads first.
// However, defining the entire object here is simpler for this request.
// window.ASCII_ART.titanMegaBoss = [ ... ]; // Already included above
// window.ASCII_ART.titanMegaBoss_avatar = [ ... ]; // Already included above
// window.ASCII_ART.serpentLaserProjectile = [ ... ]; // Already included above

console.log("ASCII_ART object initialized globally.");
// quoteBanner.js

console.log("quoteBanner.js loaded. Waiting for game initialization...");

// Define a list of quotes
const QUOTES = [
    "Stay sharp, pilot. The void is unforgiving.",
    "Sector clear... for now. Stay vigilant.",
    "Trust your shields. They're your last hope.",
    "Lasers cut through doubt and alien hulls.",
    "Keep moving. A still target is a dead target.",
    "Score isn't everything, but it helps.",
    "Augmentation is the path to survival.",
    "Don't dwell on the past. Focus forward.",
    "Embrace the chaos, command the fight.",
    "The stars are watching. Make them proud.",
    "Systems nominal. Time to engage.",
    "Warning: High enemy concentration detected.",
    "Analyzing threat patterns...",
    "This unit is augmented and ready.",
    "Prioritize targets. Eliminate the threat."
];

// Function to combine player avatar and quote into a banner art array
function createQuoteBannerArt(quoteText, playerArt, playerName, gameWidth) {
    const avatarHeight = playerArt ? playerArt.length : 3;
    const avatarWidth = playerArt && playerArt[0] ? playerArt[0].length : 7;
    const quoteMaxWidth = 45; // Max width for the quote text block
    const padding = 2; // Padding inside the border
    const separatorWidth = 3; // Space/separator between avatar and quote
    const minBannerWidth = 40; // Minimum width
    const borderChar = "─";
    const cornerTL = "╭", cornerTR = "╮", cornerBL = "╰", cornerBR = "╯";
    const borderV = "│";

    // Simple text wrapping
    const lines = [];
    let currentLine = "";
    const words = quoteText.split(/\s+/); // Split by one or more whitespace
    for (const word of words) {
        if (currentLine.length + word.length + (currentLine === "" ? 0 : 1) > quoteMaxWidth) {
            lines.push(currentLine);
            currentLine = word;
        } else {
            if (currentLine !== "") currentLine += " ";
            currentLine += word;
        }
    }
    if (currentLine !== "") lines.push(currentLine);

    const quoteHeight = lines.length;
    const contentHeight = Math.max(avatarHeight, quoteHeight);
    const totalHeight = contentHeight + padding * 2 + 2; // Content + Padding + Borders (- -)

    // Calculate dynamic width based on content, capped by gameWidth
    const quoteBlockWidth = lines.reduce((max, line) => Math.max(max, line.length), 0);
    const minContentWidth = Math.max(avatarWidth + separatorWidth + quoteBlockWidth, minBannerWidth - padding * 2 - 2);
    const totalContentWidth = Math.min(gameWidth - padding * 2 - 2, minContentWidth);

    const bannerArt = [];
    const borderH = borderChar.repeat(totalContentWidth);
    bannerArt.push(cornerTL + borderH + cornerTR);

    const avatarPadTop = Math.floor((contentHeight - avatarHeight) / 2);
    const quotePadTop = Math.floor((contentHeight - quoteHeight) / 2);

    for (let i = 0; i < contentHeight; i++) {
        let line = borderV; // Left border
        line += " ".repeat(padding); // Left padding

        // Add avatar or padding
        if (i >= avatarPadTop && i < avatarPadTop + avatarHeight && playerArt && playerArt[i - avatarPadTop]) {
             line += playerArt[i - avatarPadTop].padEnd(avatarWidth, ' ');
        } else {
             line += " ".repeat(avatarWidth);
        }

        line += " ".repeat(separatorWidth); // Separator space

        // Add quote line or padding
        if (i >= quotePadTop && i < quotePadTop + quoteHeight && lines[i - quotePadTop]) {
            line += lines[i - quotePadTop].padEnd(quoteMaxWidth, ' ');
        } else {
            line += " ".repeat(quoteMaxWidth);
        }

        // Trim quote section to total content width and add right padding/border
        line = line.substring(0, totalContentWidth + padding + 1); // Cut to calculated content width + left border + left padding
        line += " ".repeat(totalContentWidth + padding + 1 - line.length); // Add any needed space if line is shorter (due to max width cap)
        line += " ".repeat(padding); // Right padding
        line += borderV; // Right border

        bannerArt.push(line);
    }

    bannerArt.push(cornerBL + borderH + cornerBR);

    // Optional: Add player name below the quote block inside the banner
    const nameText = `- ${playerName} -`;
    // Find the line just below the quote block within the banner
    const nameLineIndex = padding + quotePadTop + quoteHeight;
    if(nameLineIndex < contentHeight + padding) { // Check if there's space within the content area + padding
         if(nameText.length <= quoteMaxWidth) {
            const namePadLeft = " ".repeat(Math.floor((quoteMaxWidth - nameText.length) / 2));
            // Construct the line for the name, aligning it correctly
            let nameLine = borderV;
            nameLine += " ".repeat(padding);
            nameLine += " ".repeat(avatarWidth + separatorWidth); // Space past avatar section
            nameLine += namePadLeft + nameText.padEnd(quoteMaxWidth - namePadLeft.length, ' '); // Centered name in quote width
            nameLine = nameLine.substring(0, totalContentWidth + padding + 1); // Trim if necessary
            nameLine += " ".repeat(totalContentWidth + padding + 1 - nameLine.length);
            nameLine += " ".repeat(padding);
            nameLine += borderV;

            // Replace the corresponding line in the banner art
            // Need to adjust index based on border/padding lines
            bannerArt[1 + nameLineIndex] = nameLine; // 1 for top border
         }
    }


    return bannerArt;
}

// Function to add a random quote banner to the game state
function addRandomQuoteBanner() {
    // Check if gameLogic is available and game is not over
    // window.gameLogicInstance is made global by the main script
    if (!window.gameLogicInstance || !window.gameLogicInstance.state || window.gameLogicInstance.state.gameOver) {
        return;
    }

    const gameState = window.gameLogicInstance.state;
    // ASCII_ART is a top-level constant in the main script, likely accessible globally
    const ASCII_ART = window.ASCII_ART;
    const GAME_WIDTH = window.GAME_WIDTH || 80; // Use global GAME_WIDTH

    // Don't show if other important banners are active
    // Check if any banner is NOT of type 'talking' (initial messages) or 'quote' (our custom type)
    if (gameState.activeBanners && gameState.activeBanners.some(b => b.type !== 'talking' && b.type !== 'quote')) {
         console.log("Skipping quote banner - Important banner active.");
         return;
    }
    // Also limit the number of simultaneous quote banners
    if (gameState.activeBanners.filter(b => b.type === 'quote').length > 0) {
         console.log("Skipping quote banner - Another quote banner active.");
         return;
    }


    // Pick a random quote
    const randomQuote = QUOTES[Math.floor(Math.random() * QUOTES.length)];

    // Get player info - ensure player object exists before accessing properties
    const playerArt = (gameState.player && ASCII_ART.player_avatar) ? ASCII_ART.player_avatar : ["???", "(?)", "'-'"]; // Fallback art
    const playerName = (gameState.player && gameState.hudName) ? gameState.hudName : "Unknown Pilot"; // Fallback name

    // Create the banner art
    const bannerArt = createQuoteBannerArt(randomQuote, playerArt, playerName, GAME_WIDTH);

    // Add the banner to the game state
    // The existing addBanner function in GameState expects art and textFallback.
    // It also handles positioning and duration based on type and speed.
    // We'll use a custom type 'quote' and let the existing banner logic handle movement.
    // The 'talking' type in the original code has custom typing animation logic,
    // we'll let this custom banner just slide in and out using a speed > 0.

    // Use the game's own addBanner method if available, it handles banner object structure correctly.
    // If not, manually add, but relying on game's method is safer.
    if (typeof gameState.addBanner === 'function') {
        // gameState.addBanner(art, textFallback, type = "standard")
        gameState.addBanner(bannerArt, randomQuote, "quote"); // Use the custom 'quote' type
        console.log("Added quote banner via addBanner:", randomQuote);
    } else {
        // Fallback if addBanner method doesn't exist (less ideal)
        const bannerHeight = bannerArt.length;
        const bannerWidth = bannerArt[0] ? bannerArt[0].length : quoteMaxWidth + avatarWidth + separatorWidth + padding * 2 + 2;
        gameState.activeBanners.push({
           art: bannerArt,
           text: randomQuote,
           pos: new Vector2(GAME_WIDTH, Math.floor((window.GAME_HEIGHT - bannerHeight) / 2)),
           speed: 0.5, // Slower slide-in animation
           duration: Math.floor((GAME_WIDTH + bannerWidth) / 0.5) + 300, // Duration to cross screen + display time
           type: 'quote', // Custom type for identification if needed elsewhere
           // The existing renderer's 'drawBanners' function handles non-'talking' types by just drawing the 'art'
           // The existing 'updateBanners' function handles duration and horizontal movement based on 'speed'
           // This should work with minimal changes to the main game logic/renderer.
        });
        console.log("Manually added quote banner:", randomQuote);
    }
}

// --- Scheduling ---
// Periodically check if we should show a banner.
// Use setInterval for simplicity in an external script.
const checkInterval = 5000; // Check every 5 seconds
const chancePerInterval = 0.15; // 15% chance each time we check

let quoteBannerTimer = setInterval(() => {
    // Only attempt if gameLogicInstance and gameState are available
    if (window.gameLogicInstance && window.gameLogicInstance.state) {
        // Add some randomness to prevent banners at fixed intervals
        if (Math.random() < chancePerInterval) {
            addRandomQuoteBanner();
        }
    } else {
        // If gameLogicInstance isn't ready after a long time, something is wrong.
        // Stop the timer or log an error if needed.
        // console.log("Game logic not ready for quote banners...");
        // Potentially add a check here to clear the interval if too much time passes
    }
}, checkInterval);

// Optional: Clear the timer if the game ends, though not strictly necessary for this effect
// This would require hooking into a game over event or checking gameState.gameOver within the timer.
// For simplicity, we'll let it run, it just won't add banners if state.gameOver is true.

console.log("quoteBanner.js setup complete. Scheduling checks.");
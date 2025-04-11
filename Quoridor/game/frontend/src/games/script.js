let team = "NONE";

// Creates a new game with the user-selected settings
async function createGame() {
    const size = document.getElementById("board-size-input").value;
    const nbWalls = document.getElementById("number-walls-input").value;
    const turnStart = team;
    const ai = false;

    const response = await fetch(`${backendURL}/game`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        },
        body: JSON.stringify({ size, nbWalls, turnStart, ai })
    });

    if (response.ok) {
        const json = await response.json();
        const joinedGame = JSON.parse(sessionStorage.getItem("joinedGame")) || [];
        joinedGame.push(json.UUID);
        sessionStorage.setItem("joinedGame", JSON.stringify(joinedGame));
        document.location.href = `../game?uuid=${json.UUID}`;
    } else {
        location.reload();
    }
}

// Navigation functions
const navigateBack = () => document.location.href = "../";
const navigateHome = () => document.location.href = "../";

// Updates the board size value display
const boardSizeOutput = () => {
    document.getElementById("board-size-output").innerText = document.getElementById("board-size-input").value;
};

// Updates the wall number value display
const numberWallsOutput = () => {
    document.getElementById("number-walls-output").innerText = document.getElementById("number-walls-input").value;
};

// Selects the starting team (random, dolphin, or shark)
function selectTeam(selection) {
    team = selection;
    const [randomBtn, dolphinBtn, sharkBtn] = ["team-random", "team-dolphin", "team-shark"].map(id => document.getElementById(id));

    randomBtn.classList.toggle("clicked", selection === "NONE");
    dolphinBtn.classList.toggle("clicked", selection === "FIRST");
    sharkBtn.classList.toggle("clicked", selection === "SECOND");
}

// Creates a cell element for the game board
function createCell(UUID, x, y) {
    const el = document.createElement("div");
    el.className = "cell";
    el.id = `cell-${UUID}-${x}-${y}`;
    return el;
}

// Creates a horizontal wall element for the game board
function createHorizontalWall(UUID, x, y, size) {
    const el = document.createElement("div");
    el.className = "horizontal-wall";
    if (y !== 0) el.classList.add(`horizontal-wall-${UUID}-${x}-${y - 1}`);
    if (y !== size - 1) el.classList.add(`horizontal-wall-${UUID}-${x}-${y}`);
    return el;
}

// Creates a vertical wall element for the game board
function createVerticalWall(UUID, x, y, size) {
    const el = document.createElement("div");
    el.className = "vertical-wall";
    if (x !== 0) el.classList.add(`vertical-wall-${UUID}-${x - 1}-${y}`);
    if (x !== size - 1) el.classList.add(`vertical-wall-${UUID}-${x}-${y}`);
    return el;
}

// Creates a corner element for the game board
function createCorner(UUID, x, y) {
    const el = document.createElement("div");
    el.className = "corner";
    el.id = `corner-${UUID}-${x}-${y}`;
    return el;
}

// List of element creation functions indexed by cell/wall/corner type
const createElement = [createCell, createVerticalWall, createHorizontalWall, createCorner];

// Creates the information panel for a game
function createInformation(UUID) {
    const info = document.createElement("div");
    info.className = "game-information";
    info.id = `game-information-${UUID}`;

    for (let i = 0; i < 2; i++) {
        const player = document.createElement("div");
        player.className = `game-player-${i + 1}`;

        const img = document.createElement("img");
        img.src = `../player_${i + 1}.png`;
        img.alt = `player_${i + 1}`;

        const username = document.createElement("div");
        username.className = `game-player-${i + 1}-username`;
        username.id = `game-player-${i + 1}-username-${UUID}`;

        player.append(img, username);
        info.appendChild(player);
    }

    const status = document.createElement("div");
    status.className = "game-status";
    status.id = `game-status-${UUID}`;

    const buttons = document.createElement("div");
    buttons.className = "game-buttons";

    const joinBtn = document.createElement("button");
    joinBtn.className = "game-join-button";
    joinBtn.id = `game-join-button-${UUID}`;
    joinBtn.innerText = "Join";
    joinBtn.addEventListener("click", () => join(UUID));

    const spectateBtn = document.createElement("button");
    spectateBtn.className = "game-spectate-button";
    spectateBtn.id = `game-spectate-button-${UUID}`;
    spectateBtn.innerText = "Spectate";
    spectateBtn.addEventListener("click", () => spectate(UUID));

    buttons.append(joinBtn, spectateBtn);
    info.append(status, buttons);

    return info;
}

// Fetches the list of available games from the API
async function getGames() {
    const response = await fetch(`${backendURL}/games`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        }
    });
    if (!response.ok) {
        document.location.href = "../";
        return;
    }
    return await response.json();
}

// Renders a single game board in the UI
function generate(game) {
    const gameWrap = document.createElement("div");
    gameWrap.className = "game";

    const gameBoard = document.createElement("div");
    gameBoard.className = "game-board";
    gameBoard.id = `game-board-${game.UUID}`;
    const boardSize = game.board.size;
    gameBoard.style.gridTemplateColumns = `repeat(${boardSize * 2 - 1}, auto)`;
    gameBoard.style.gridTemplateRows = `repeat(${boardSize * 2 - 1}, auto)`;

    for (let i = 0; i < boardSize * 2 - 1; i++) {
        for (let j = 0; j < boardSize * 2 - 1; j++) {
            const fn = createElement[i % 2 * 2 + j % 2];
            gameBoard.appendChild(fn(game.UUID, Math.floor(i / 2), Math.floor(j / 2), boardSize));
        }
    }

    gameWrap.appendChild(gameBoard);
    gameWrap.appendChild(createInformation(game.UUID));

    const gamesContainer = document.getElementById("join-page");
    gamesContainer.appendChild(gameWrap);

    game.board.positions.forEach((pos, index) => {
        const cell = document.getElementById(`cell-${game.UUID}-${pos.x}-${pos.y}`);
        const player = document.createElement("div");
        player.className = "player";
        player.id = `player-${index + 1}-${game.UUID}`;

        const img = document.createElement("img");
        img.src = `../player_${index + 1}.png`;
        img.alt = `player_${index + 1}`;

        player.appendChild(img);
        cell.appendChild(player);
    });
}

// Renders all games and attaches UI input listeners
function generates(games) {
    for (let game of games) generate(game);

    select(window.location.hash.substring(1));

    boardSizeOutput();
    document.getElementById("board-size-input").addEventListener("input", boardSizeOutput);

    numberWallsOutput();
    document.getElementById("number-walls-input").addEventListener("input", numberWallsOutput);
}

// Joins a game by sending a request to the backend
async function join(UUID) {
    const joinedGame = JSON.parse(sessionStorage.getItem("joinedGame")) || [];
    if (!joinedGame.includes(UUID)) {
        joinedGame.push(UUID);
        sessionStorage.setItem("joinedGame", JSON.stringify(joinedGame));
        const response = await fetch(`${backendURL}/game/${UUID}/join`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Player-UUID": sessionStorage.getItem("playerID")
            }
        });
        if (!response.ok) return location.reload();
    }
    document.location.href = `../game?uuid=${UUID}`;
}

// Periodically fetches and updates the game list
async function getAndDisplay() {
    const games = await getGames();
    display(games);
}

// Opens a game in spectator mode
function spectate(UUID) {
    document.location.href = `../game?uuid=${UUID}`;
}

// Updates the display of available games and their current state
function display(games) {
    for (const game of games) {
        // Generate the game board if it doesn't already exist
        if (!document.getElementById(`game-board-${game.UUID}`)) {
            generate(game);
        }

        // Place players on their respective cells
        game.board.positions.forEach((pos, index) => {
            const cell = document.getElementById(`cell-${game.UUID}-${pos.x}-${pos.y}`);
            const player = document.getElementById(`player-${index + 1}-${game.UUID}`);
            if (player && cell) cell.appendChild(player);
        });

        // Clear previously placed walls
        document.querySelectorAll(`.placed-${game.UUID}`).forEach(wall => {
            wall.classList.remove(`placed-${game.UUID}`, "placed");
        });

        // Re-add placed walls based on the game state
        for (let i = 0; i < game.board.size - 1; i++) {
            for (let j = 0; j < game.board.size - 1; j++) {
                const type = game.board.walls[i][j];
                if (type === "VERTICAL") {
                    document.querySelectorAll(`.vertical-wall-${game.UUID}-${i}-${j}`)
                        .forEach(w => w.classList.add(`placed-${game.UUID}`, "placed"));
                    const corner = document.getElementById(`corner-${game.UUID}-${i}-${j}`);
                    if (corner) corner.classList.add(`placed-${game.UUID}`, "placed");
                }
                if (type === "HORIZONTAL") {
                    document.querySelectorAll(`.horizontal-wall-${game.UUID}-${i}-${j}`)
                        .forEach(w => w.classList.add(`placed-${game.UUID}`, "placed"));
                    const corner = document.getElementById(`corner-${game.UUID}-${i}-${j}`);
                    if (corner) corner.classList.add(`placed-${game.UUID}`, "placed");
                }
            }
        }

        // Update player usernames
        for (let i = 0; i < 2; i++) {
            const usernameEl = document.getElementById(`game-player-${i + 1}-username-${game.UUID}`);
            if (usernameEl) usernameEl.innerText = game.usernames[i];
        }

        // Update game status
        const status = document.getElementById(`game-status-${game.UUID}`);
        const gameInfo = document.getElementById(`game-information-${game.UUID}`);

        const isJoined = (JSON.parse(sessionStorage.getItem("joinedGame")) || []).includes(game.UUID);
        if (isJoined) {
            document.getElementById(`game-spectate-button-${game.UUID}`).style.display = "none";
        }

        if (game.usernames.includes(null)) {
            status.innerText = "Waiting...";
            gameInfo.classList.add("permanant");
        } else {
            if (!isJoined) {
                document.getElementById(`game-join-button-${game.UUID}`).style.display = "none";
            }
            if (game.winner !== "NONE") {
                status.innerText = "Game over!";
                gameInfo.classList.add("permanant");
            } else {
                status.innerText = "Running...";
                gameInfo.classList.remove("permanant");
            }
        }
    }
}

// Switches between the create and join tabs
function select(tab) {
    const createTab = document.getElementById("menu-create");
    const createPage = document.getElementById("create-page");
    const joinTab = document.getElementById("menu-join");
    const joinPage = document.getElementById("join-page");

    if (tab.toLowerCase() === "create") {
        if (!createTab.classList.contains("selected")) {
            createTab.classList.add("selected");
            createPage.classList.remove("disable");

            joinTab.classList.remove("selected");
            joinPage.classList.add("disable");
        }
    } else {
        if (!joinTab.classList.contains("selected")) {
            joinTab.classList.add("selected");
            joinPage.classList.remove("disable");

            createTab.classList.remove("selected");
            createPage.classList.add("disable");
        }
    }
}

// Main entry point: fetches and displays games, then refreshes periodically
async function main() {
    const games = await getGames();
    generates(games);
    display(games);
    setInterval(getAndDisplay, 1000);
}

main();

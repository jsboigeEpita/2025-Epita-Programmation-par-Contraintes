let size; // Size of the game board (number of rows/columns)
let walls; // 2D array storing wall placement information
let positions; // Array storing the current positions of both players
let nbWalls; // Array storing the number of remaining walls for each player
let turn; // Current turn ('PLAYER_1' or 'PLAYER_2')
let usernames; // Usernames of the two players
let winner; // Winner of the game ('PLAYER_1', 'PLAYER_2', or 'NONE')
let winnerIsDisplayed = false; // Flag to check if the winner screen has been shown
let isYourTurn; // Boolean indicating if it is the current client's turn

// Mapping player identifier to their index in the positions and nbWalls arrays
const turnToInteger = {
    PLAYER_1: 0,
    PLAYER_2: 1
};

// Mapping each direction to its opposite (used for movement logic)
const oppositeDirection = {
    UP: 'DOWN',
    RIGHT: 'LEFT',
    DOWN: 'UP',
    LEFT: 'RIGHT'
};

// Mapping direction strings to their respective wall check functions
const directionToIsWall = {
    UP: isWallUp,
    RIGHT: isWallRight,
    DOWN: isWallDown,
    LEFT: isWallLeft
};

// Coordinate offset for each direction (used to calculate new positions)
const directionToCoordinate = {
    UP: { x: -1, y: 0 },
    RIGHT: { x: 0, y: 1 },
    DOWN: { x: 1, y: 0 },
    LEFT: { x: 0, y: -1 },
}

// Converts a coordinate offset into a direction string
function coordinateToDirection(coordinate) {
    for (let direction of ["UP", "RIGHT", "DOWN", "LEFT"]) {
        if (coordinate.x === directionToCoordinate[direction].x && coordinate.y === directionToCoordinate[direction].y) {
            return direction;
        }
    }
    return undefined;
}

// Checks whether a position is within the board boundaries
function isInBoard(position) {
    return position.x >= 0 && position.x < size &&
           position.y >= 0 && position.y < size;
}  

// Checks for a horizontal wall above the current coordinate
function isWallUp(coordinate) {
    if (coordinate.x !== 0 && coordinate.y !== 0 &&
        walls[coordinate.x - 1][coordinate.y - 1] === 'HORIZONTAL') {
        return true;
    }
    return coordinate.x !== 0 && coordinate.y !== size - 1 &&
        walls[coordinate.x - 1][coordinate.y] === 'HORIZONTAL';
}  

// Checks for a vertical wall to the right of the current coordinate
function isWallRight(coordinate) {
    if (coordinate.x !== 0 && coordinate.y !== size - 1 &&
        walls[coordinate.x - 1][coordinate.y] === 'VERTICAL') {
        return true;
    }
    return coordinate.x !== size - 1 && coordinate.y !== size - 1 &&
        walls[coordinate.x][coordinate.y] === 'VERTICAL';
}  

// Checks for a horizontal wall below the current coordinate
function isWallDown(coordinate) {
    if (coordinate.x !== size - 1 && coordinate.y !== size - 1 &&
        walls[coordinate.x][coordinate.y] === 'HORIZONTAL') {
        return true;
    }
    return coordinate.x !== size - 1 && coordinate.y !== 0 &&
        walls[coordinate.x][coordinate.y - 1] === 'HORIZONTAL';
}  

// Checks for a vertical wall to the left of the current coordinate
function isWallLeft(coordinate) {
    if (coordinate.x !== size - 1 && coordinate.y !== 0 &&
        walls[coordinate.x][coordinate.y - 1] === 'VERTICAL') {
        return true;
    }
    return coordinate.x !== 0 && coordinate.y !== 0 &&
        walls[coordinate.x - 1][coordinate.y - 1] === 'VERTICAL';
}

// Determines whether a move can be made in a given direction from a given position
function canSimpleMove(position, direction) {
    // If there's a wall in the specified direction, return false
    if (directionToIsWall[direction](position)) return false;

    // Compute the new position based on the direction
    const dir = directionToCoordinate[direction];
    const projectionPosition = { x: position.x + dir.x, y: position.y + dir.y };

    // Check that the projected position is within board boundaries
    return isInBoard(projectionPosition);
}

// Determines if a player can move in a specific direction, possibly jumping over the opponent
function canMove(direction, jump) {
    const current = positions[turnToInteger[turn]]; // Current player's position
    const provisional = { ...current }; // Copy of current position
    const opponent = positions[(turnToInteger[turn] + 1) % 2]; // Opponent's position

    if (jump) {
        // Calculate the difference in position between current player and opponent
        const difference = { x: opponent.x - provisional.x, y: opponent.y - provisional.y };

        // Make sure the players are adjacent (1 cell apart)
        if (difference.x * difference.x + difference.y * difference.y !== 1) return false;

        const differenceDirection = coordinateToDirection(difference);

        // Disallow jumping backward
        if (oppositeDirection[differenceDirection] === direction) return false;

        // Check if there's a wall blocking the jump
        if (directionToIsWall[differenceDirection](provisional)) return false;

        // Simulate jump forward
        provisional.x += difference.x;
        provisional.y += difference.y;

        // Check if the position behind opponent is available
        if (canSimpleMove(provisional, differenceDirection))
            return differenceDirection === direction;
    }

    // Check if we can move normally
    if (!canSimpleMove(provisional, direction)) return false;

    // Apply movement
    provisional.x += directionToCoordinate[direction].x;
    provisional.y += directionToCoordinate[direction].y;

    // Make sure we're not stepping onto the opponent's square (unless jumping)
    return (provisional.x !== opponent.x || provisional.y !== opponent.y);
}

// Executes the player's move and sends the move to the server
async function move(direction, jump) {
    if (jump) {
        // Move directly to opponent's position when jumping
        positions[turnToInteger[turn]].x = positions[(turnToInteger[turn] + 1) % 2].x;
        positions[turnToInteger[turn]].y = positions[(turnToInteger[turn] + 1) % 2].y;
    }

    // Move in the specified direction
    positions[turnToInteger[turn]].x += directionToCoordinate[direction].x;
    positions[turnToInteger[turn]].y += directionToCoordinate[direction].y;

    isYourTurn = false; // End the player's turn
    display(); // Refresh the UI

    // Send the move to the backend server
    const gameID = new URLSearchParams(window.location.search).get("uuid");
    const response = await fetch(`${backendURL}/game/${gameID}/move`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        },
        body: JSON.stringify({
            direction,
            jump
        })
    });

    // If server rejects the move, reload the game state
    if (!response.ok) {
        location.reload();
    }
}

// Checks if a wall coordinate is within the bounds of the wall grid (excluding outer edge)
function isInWallMap(position) {
    return position.x >= 0 && position.x < size - 1 &&
           position.y >= 0 && position.y < size - 1;
}

// Returns a deep copy of the current game state (to simulate and rollback moves)
function cloneBoardState() {
    return {
        size,
        walls: walls.map(row => [...row]), // Deep copy of 2D array
        positions: positions.map(p => ({ ...p })), // Deep copy of player positions
        nbWalls: [...nbWalls], // Copy of walls left
        turn
    };
}

// Restores a previously saved game state (undo simulation)
function restoreBoardState(state) {
    size = state.size;
    walls = state.walls.map(row => [...row]);
    positions = state.positions.map(p => ({ ...p }));
    nbWalls = [...state.nbWalls];
    turn = state.turn;
}

// Checks if both players can still reach their goal (top or bottom row)
function canWin() {
    for (let i = 0; i < 2; i++) {
        let canPlayerWin = false;

        // Initialize a visited matrix
        const mark = Array.from({ length: size }, () =>
            Array.from({ length: size }, () => false)
        );

        const queue = [positions[i]]; // Start BFS from current player's position
        mark[positions[i].x][positions[i].y] = true;

        while (queue.length > 0) {
            const position = queue.shift();

            // Goal for player 0 is bottom row (x == size - 1), for player 1 is top row (x == 0)
            if (position.x === i * (size - 1)) {
                canPlayerWin = true;
                break;
            }

            // Check all 4 directions
            for (const dir in directionToCoordinate) {
                if (canSimpleMove(position, dir)) {
                    const delta = directionToCoordinate[dir];
                    const newPos = { x: position.x + delta.x, y: position.y + delta.y };
                    if (!mark[newPos.x][newPos.y]) {
                        queue.push(newPos);
                        mark[newPos.x][newPos.y] = true;
                    }
                }
            }
        }

        // If either player cannot reach their goal, return false
        if (!canPlayerWin) return false;
    }

    return true;
}

// Validates if a wall can be legally placed at the specified position
function canPlace(position, wall) {
    // Check basic placement conditions
    if (!isInWallMap(position) || wall === 'NONE') return false;
    if (nbWalls[turnToInteger[turn]] <= 0) return false;
    if (walls[position.x][position.y] !== 'NONE') return false;
    if (winner !== "NONE") return false;
    if (!isYourTurn) return false;
    if (document.getElementById(`player-${turnToInteger[turn] + 1}`).classList.contains("selected")) return false;
    if (usernames[0] == null || usernames[1] == null) return false;

    // Simulate placing the wall and check if both players can still win
    const savedState = cloneBoardState();
    walls[position.x][position.y] = wall;
    const valid = canWin();
    restoreBoardState(savedState);
    if (!valid) return false;

    // Prevent placing adjacent parallel walls
    if (wall === 'HORIZONTAL') {
        const left = position.y !== 0 && walls[position.x][position.y - 1] === 'HORIZONTAL';
        const right = position.y !== size - 2 && walls[position.x][position.y + 1] === 'HORIZONTAL';
        return !(left || right);
    } else {
        const up = position.x !== 0 && walls[position.x - 1][position.y] === 'VERTICAL';
        const down = position.x !== size - 2 && walls[position.x + 1][position.y] === 'VERTICAL';
        return !(up || down);
    }
}

// Attempts to place a wall on the board, with fallback to alternative options
async function place(x, y, wall, alt) {
    // Try placing the wall directly if it's valid
    if (canPlace({x: x, y: y}, wall)) {
        nbWalls[turnToInteger[turn]] = nbWalls[turnToInteger[turn]] - 1; // Reduce remaining walls
        walls[x][y] = wall; // Place the wall
        isYourTurn = false; // End current player's turn
        display(); // Update the UI

        // Send the placement to the backend server
        const gameID = new URLSearchParams(window.location.search).get("uuid");
        const response = await fetch(`${backendURL}/game/${gameID}/place`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Player-UUID": sessionStorage.getItem("playerID")
            },
            body: JSON.stringify({ x, y, wall })
        });

        // Reload page if the server responds with an error
        if (!response.ok) {
            location.reload();
        }
    }
    // Try an alternate placement option if provided
    else if (alt !== null) {
        if (alt === "HORIZONTAL" || alt === "VERTICAL") {
            wall = alt; // Change orientation
        }
        else if (wall === "HORIZONTAL") {
            y = y + alt; // Shift wall horizontally
        }
        else {
            x = x + alt; // Shift wall vertically
        }

        // Try placing with the updated values
        if (canPlace({x: x, y: y}, wall)) {
            nbWalls[turnToInteger[turn]] = nbWalls[turnToInteger[turn]] - 1;
            walls[x][y] = wall;
            isYourTurn = false;
            display();

            const gameID = new URLSearchParams(window.location.search).get("uuid");
            const response = await fetch(`${backendURL}/game/${gameID}/place`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Player-UUID": sessionStorage.getItem("playerID")
                },
                body: JSON.stringify({ x, y, wall })
            });

            if (!response.ok) {
                location.reload();
            }
        }
    }
}

// Selects a cell to initiate or confirm a move for the current player
function select(x, y) {
    const player = document.getElementById(`player-${turnToInteger[turn] + 1}`);
    const cell = document.getElementById(`cell-${x}-${y}`);
    const position = positions[turnToInteger[turn]];

    if (winner !== "NONE") return; // Do nothing if game is over
    if (!isYourTurn) return; // Ignore input if it's not your turn
    if (usernames[0] == null || usernames[1] == null) return false;

    // If player is already selected, try to move to the clicked cell
    if (player.classList.contains("selected")) {
        if (cell.classList.contains("selected")) {
            deSelect();
            if ((position.x - x) ** 2 + (position.y - y) ** 2 === 1) {
                coordinate = positions[(turnToInteger[turn]) % 2];
            }
            else {
                coordinate = positions[(turnToInteger[turn] + 1) % 2];
            }
            coordinate = { x: x - coordinate.x, y: y - coordinate.y };
            move(coordinateToDirection(coordinate), (position.x - x) ** 2 + (position.y - y) ** 2 !== 1)
        } else {
            deSelect();
        }
    }
    // If player not selected yet, select them and highlight available moves
    else {
        if (x === position.x && y === position.y) {
            if (!player.classList.contains("selected")) {
                player.className = player.className + " selected";
            }

            for (let direction of ["UP", "RIGHT", "DOWN", "LEFT"]) {
                if (canMove(direction, true)) {
                    coordinate = positions[(turnToInteger[turn] + 1) % 2];
                    dir = directionToCoordinate[direction];
                    coordinate = { x: coordinate.x + dir.x, y: coordinate.y + dir.y };
                    const selectedCell = document.getElementById(`cell-${coordinate.x}-${coordinate.y}`);
                    if (!selectedCell.classList.contains("selected")) {
                        selectedCell.className = selectedCell.className + " selected";
                    }
                }
                if (canMove(direction, false)) {
                    coordinate = positions[turnToInteger[turn]];
                    dir = directionToCoordinate[direction];
                    coordinate = { x: coordinate.x + dir.x, y: coordinate.y + dir.y };
                    const selectedCell = document.getElementById(`cell-${coordinate.x}-${coordinate.y}`);
                    if (!selectedCell.classList.contains("selected")) {
                        selectedCell.className = selectedCell.className + " selected";
                    }
                }
            }
        }
    }
}

// Clears all currently selected cells and player
function deSelect() {
    const elements = Array.from(document.getElementsByClassName("selected"));
    elements.forEach(element => element.classList.remove("selected"));
}

// Highlights wall segments and corner when hovering over a possible wall placement
function hoverWall(x, y, wall, alt) {
    if (canPlace({ x: x, y: y }, wall)) {
        let walls = Array.from(document.getElementsByClassName(`${wall.toLowerCase(wall)}-wall-${x}-${y}`));
        walls.forEach(wall => {
            if (!wall.classList.contains("hovered")) wall.className = wall.className + " hovered"
        });
        corner = document.getElementById(`corner-${x}-${y}`);
        if (!corner.classList.contains("hovered")) {
            corner.className = corner.className + " hovered";
        }
    }
    else if (alt !== null) {
        if (alt === "HORIZONTAL" || alt === "VERTICAL") {
            wall = alt;
        }
        else if (wall === "HORIZONTAL") {
            y = y + alt;
        }
        else {
            x = x + alt;
        }
        if (canPlace({ x: x, y: y }, wall)) {
            let walls = Array.from(document.getElementsByClassName(`${wall.toLowerCase(wall)}-wall-${x}-${y}`));
            walls.forEach(wall => {
                if (!wall.classList.contains("hovered")) wall.className = wall.className + " hovered"
            });
            corner = document.getElementById(`corner-${x}-${y}`);
            if (!corner.classList.contains("hovered")) {
                corner.className = corner.className + " hovered";
            }
        }
    }
}

// Removes all hover highlights from wall elements
function deHoverWall() {
    Array.from(document.getElementsByClassName("horizontal-wall")).forEach(horizontalWall => horizontalWall.classList.remove("hovered"));
    Array.from(document.getElementsByClassName("vertical-wall")).forEach(verticalWall => verticalWall.classList.remove("hovered"));
    Array.from(document.getElementsByClassName("corner")).forEach(corner => corner.classList.remove("hovered"));
}

// Creates a playable cell on the game board at coordinates (x, y)
function createCell(x, y) {
    const element = document.createElement("div");
    element.className = "cell";
    element.id = `cell-${x}-${y}`;
    element.addEventListener("click", () => select(x, y));
    return element;
}

// Creates a horizontal wall element between cells, including click and hover interaction
function createHorizontalWall(x, y) {
    const element = document.createElement("div");
    element.className = "horizontal-wall";
    for (let i = 0; i < 2; i++) {
        const innerWall = document.createElement("div");
        innerWall.className = "half-horizontal-wall";
        innerWall.addEventListener("click", () => place(x, y - 1 + i, "HORIZONTAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseenter", () => hoverWall(x, y - 1 + i, "HORIZONTAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseleave", () => deHoverWall());
        element.appendChild(innerWall);
    }
    // Assign appropriate wall classes for positioning and highlighting
    if (y == 0) {
        element.className += ` horizontal-wall-${x}-${y}`;
    } else if (y == size - 1) {
        element.className += ` horizontal-wall-${x}-${y - 1}`;
    } else {
        element.className += ` horizontal-wall-${x}-${y} horizontal-wall-${x}-${y - 1}`;
    }
    return element;
}

// Creates a vertical wall element between cells, including click and hover interaction
function createVerticalWall(x, y) {
    const element = document.createElement("div");
    element.className = "vertical-wall";
    for (let i = 0; i < 2; i++) {
        const innerWall = document.createElement("div");
        innerWall.className = "half-vertical-wall";
        innerWall.addEventListener("click", () => place(x - 1 + i, y, "VERTICAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseenter", () => hoverWall(x - 1 + i, y, "VERTICAL", (i + 1) % 2 * 2 - 1));
        innerWall.addEventListener("mouseleave", () => deHoverWall());
        element.appendChild(innerWall);
    }
    // Assign appropriate wall classes for positioning and highlighting
    if (x == 0) {
        element.className += ` vertical-wall-${x}-${y}`;
    } else if (x == size - 1) {
        element.className += ` vertical-wall-${x - 1}-${y}`;
    } else {
        element.className += ` vertical-wall-${x}-${y} vertical-wall-${x - 1}-${y}`;
    }
    return element;
}

// Creates a corner element used to place walls via SVG triangles for directional input
function createCorner(x, y) {
    const element = document.createElement("div");
    element.className = "corner";
    element.id = `corner-${x}-${y}`;
    element.wall = "none";

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("viewBox", "0 0 100 100");

    const triangles = [
        { points: "0,0 100,0 50,50", direction: "VERTICAL" },
        { points: "100,0 100,100 50,50", direction: "HORIZONTAL" },
        { points: "100,100 0,100 50,50", direction: "VERTICAL" },
        { points: "0,100 0,0 50,50", direction: "HORIZONTAL" }
    ];

    for (const triangle of triangles) {
        const polygon = document.createElementNS(svgNS, "polygon");
        polygon.setAttribute("points", triangle.points);
        polygon.addEventListener("click", () => place(x, y, triangle.direction, triangle.direction === "VERTICAL" ? "HORIZONTAL" : "VERTICAL"));
        polygon.addEventListener("mouseenter", () => hoverWall(x, y, triangle.direction, triangle.direction === "VERTICAL" ? "HORIZONTAL" : "VERTICAL"));
        polygon.addEventListener("mouseleave", () => deHoverWall());
        svg.appendChild(polygon);
    }

    element.appendChild(svg);
    return element;
}

const createElement = [
    createCell,             // index 0: standard playable cell
    createVerticalWall,     // index 1: vertical wall slot
    createHorizontalWall,   // index 2: horizontal wall slot
    createCorner            // index 3: wall intersection (corner)
];

// Generates the full game board with all cells, walls, and corners
function generate() {
    const gameBoard = document.getElementById("game-board");

    // Define grid dimensions based on board size (cells + walls)
    gameBoard.style.gridTemplateColumns = `repeat(${size * 2 - 1}, auto)`;
    gameBoard.style.gridTemplateRows = `repeat(${size * 2 - 1}, auto)`;

    // Populate grid with appropriate elements
    for (let i = 0; i < size * 2 - 1; i++) {
        for (let j = 0; j < size * 2 - 1; j++) {
            gameBoard.appendChild(createElement[i % 2 * 2 + j % 2](Math.floor(i / 2), Math.floor(j / 2)));
        }
    }

    // Add player pieces to the board
    positions.forEach((pos, index) => {
        const cell = document.getElementById(`cell-${pos.x}-${pos.y}`);
        const player = document.createElement("div");
        player.className = `player`;
        player.id = `player-${index + 1}`;
        cell.appendChild(player);

        const image = document.createElement("img");
        image.src = `../player_${index + 1}.png`;
        image.alt = `player_1`;
        player.appendChild(image);
    });
}



// Fetches the current state of the game from the backend
async function refresh() {
    const gameID = new URLSearchParams(window.location.search).get("uuid");

    const response = await fetch(`${backendURL}/game/${gameID}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-Player-UUID": sessionStorage.getItem("playerID")
        }
    });

    if (!response.ok) {
        // If the game is not found or an error occurs, go back to game list
        document.location.href = "../games";
        return;
    }

    const json = await response.json();

    // Update game state variables from backend data
    size = json.board.size;
    walls = json.board.walls;
    positions = json.board.positions;
    nbWalls = json.board.nbWalls;
    turn = json.board.turn;
    usernames = json.usernames;
    winner = json.winner;
    isYourTurn = json.isYourTurn;
}

// Updates the visual representation of the game board
function display() {
    // Move each player piece to its current position
    positions.forEach((position, index) => {
        const cell = document.getElementById(`cell-${position.x}-${position.y}`);
        cell.appendChild(document.getElementById(`player-${index + 1}`));
    });

    // Clear previously placed wall highlights
    Array.from(document.getElementsByClassName("placed")).forEach(wall => wall.classList.remove("placed"));

    // Highlight all currently placed walls on the board
    for (i = 0; i < size - 1; i++) {
        for (j = 0; j < size - 1; j++) {
            if (walls[i][j] === "VERTICAL") {
                verticalWalls = Array.from(document.getElementsByClassName(`vertical-wall-${i}-${j}`));
                verticalWalls.forEach(verticalWall => {
                    if (!verticalWall.classList.contains("placed")) {
                        verticalWall.className = verticalWall.className + " placed";
                    }
                });
                corner = document.getElementById(`corner-${i}-${j}`);
                if (!corner.classList.contains("placed")) {
                    corner.className = corner.className + " placed";
                }
            }
            if (walls[i][j] === "HORIZONTAL") {
                horizontalWalls = Array.from(document.getElementsByClassName(`horizontal-wall-${i}-${j}`));
                horizontalWalls.forEach(horizontalWall => {
                    if (!horizontalWall.classList.contains("placed")) {
                        horizontalWall.className = horizontalWall.className + " placed";
                    }
                });
                corner = document.getElementById(`corner-${i}-${j}`);
                if (!corner.classList.contains("placed")) {
                    corner.className = corner.className + " placed";
                }
            }
        }
    }

    // Update each player's name and number of remaining walls
    for (let i = 0; i < 2; i++) {
        document.getElementById(`game-player-${i + 1}-username`).innerText = usernames[i];
        document.getElementById(`game-player-${i + 1}-number-walls`).innerText = nbWalls[i] + " walls left";
    }

    // Display winner message if game is over
    if (!winnerIsDisplayed && winner != "NONE") {
        displayWinner();
    }
}

// Displays the winner screen with player info and animation
function displayWinner() {
    winnerIsDisplayed = true;
    const winnerPage = document.getElementById("winner-page");
    winnerPage.style.animation = "displayWinner 0.8s ease-out forwards";

    const winnerImage = document.getElementById("winner-image");
    winnerImage.src = `../${winner.toLowerCase()}.png`;
    winnerImage.alt = `${winner.toLowerCase()}`;

    const winnerUsername = document.getElementById("winner-username");
    winnerUsername.innerText = (winner === "PLAYER_1" ? usernames[0] : usernames[1]) + " has won the game !";

    // Add winner-specific class to style the username display
    if (!(winnerUsername.classList.contains("winner-username-1") || winnerUsername.classList.contains("winner-username-2"))) {
        winnerUsername.className = winnerUsername.className + " winner-username-" + (winner === "PLAYER_1" ? "1" : "2");
    }
}

// Disables the winner screen display
function disableWinnerPage() {
    const winnerPage = document.getElementById("winner-page");
    winnerPage.style.display = "none";
}

// Refreshes game state from server and updates the display
async function refreshAndDisplay() {
    await refresh();
    display();
}

// Main game loop initializer
async function main() {
    await refresh(); // Fetch initial state
    generate(); // Build board layout
    display(); // Render state to UI

    // Set up polling to keep UI in sync with server
    setInterval(refreshAndDisplay, 1000);
}

// Navigation function to return to game list
function navigateBack() {
    document.location.href = "../games";
}

// Navigation function to return to main homepage
function navigateHome() {
    document.location.href = "../";
}

// Launch game initialization
main();

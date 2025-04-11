const pixiContainer = document.getElementById('pixi_container')
const rgSelect = document.getElementById('rg-select')
let app = null
let container = null

eel.expose(LoadCanvas)
CANVAS_LOADED = false

// Enum for Tile type
let Tile = {
    0: 'NONE',
    1: 'ROAD',
    2: 'WATER',
    3: 'HOUSE',
    4: 'HOSPITAL',
    5: 'HARBOUR',
    6: 'SUPERMARKET',
    7: 'FACTORY',
    8: 'FIRE_STATION',
    9: 'TOWN_HALL',
    10: 'BRIDGE_ROAD'
}

// Enum for Tile texture
let TileTexture = {
    0: ['none0', 'none1', 'none2', 'none3', 'none4'],
    1: ['road'],
    2: ['water', 'water0', 'water1'],
    3: ['house', 'house0', 'house1'],
    4: ['hospital'],
    5: ['harbour'],
    6: ['supermarket'],
    7: ['factory'],
    8: ['fire_station'],
    9: ['town_hall'],
    10: ['bridge_road'],
}

async function LoadTextures() {
    for (const [key,value] of Object.entries(TileTexture)) {
        let tl = []
        for (const t of value) { 
            let te = await PIXI.Assets.load(`/images/${t}.png`)
            te.baseTexture.scaleMode = PIXI.SCALE_MODES.NEAREST;
            tl.push(te); 
        }
        TileTexture[key] = tl
    }
}

function GetTexture(type) {
    return TileTexture[type][Math.floor(Math.random() * TileTexture[type].length)];
}

async function CreateApp(width, height) {
    app = new PIXI.Application()

    await app.init({
        width: width * 32,
        height: height * 32,
        backgroundColor: 0xbbbbbb,
        antialias: false
    });

    // ------------- ZOOMING ---------------

    container = app.stage

    let s_factor = 2; // current scale
    container.scale.set(s_factor)
    const min_scale = 0.5; // min zoom
    const max_scale = 10;  // max zoom
    const z_factor = 1.1; 

    app.view.addEventListener('wheel', (e) => {
        e.preventDefault(); // not propagating
      
        const dir = e.deltaY > 0 ? 1 : -1;
        const scale_change = dir > 0 ? 1 / z_factor : z_factor; // scale change
      
        const pointer = app.renderer.events.pointer;
        const mpos = pointer.global;
      
        const wpos = {
          x: (mpos.x - container.x) / container.scale.x,
          y: (mpos.y - container.y) / container.scale.y,
        };
      
        s_factor *= scale_change;
        s_factor = Math.max(min_scale, Math.min(max_scale, s_factor)); 
        container.scale.set(s_factor);

        const spos = {
          x: wpos.x * s_factor + container.x,
          y: wpos.y * s_factor + container.y,
        };
      
        container.x -= (spos.x - mpos.x);
        container.y -= (spos.y - mpos.y);
    }, { passive: false });

    // ------------- /ZOOMING ---------------

    // ------------- DRAGGING ---------------

    let dragging = false;
    let drag_start = { x: 0, y: 0 };
    let container_start = { x: 0, y: 0 };

    app.canvas.addEventListener('mousedown', (e) => {
        dragging = true;
        drag_start.x = e.clientX;
        drag_start.y = e.clientY;
        container_start.x = container.x;
        container_start.y = container.y;
    });

    app.canvas.addEventListener('mousemove', (e) => {
        if (!dragging) return;

        const dx = e.clientX - drag_start.x;
        const dy = e.clientY - drag_start.y;

        container.x = container_start.x + dx;
        container.y = container_start.y + dy;
    });

    app.canvas.addEventListener('mouseup', () => { dragging = false; });
    app.canvas.addEventListener('mouseleave', () => { dragging = false; });

    // ------------- /DRAGGING ---------------
}

async function DestroyCanvas() {
    if (!CANVAS_LOADED)
        return

    app.destroy(true, { children: true, texture: true, baseTexture: true });
    
    await CreateApp()

    pixiContainer.classList.remove('show')
    pixiContainer.classList.add('hide')

    CANVAS_LOADED = false
}

const delay = (ms) => new Promise(res => setTimeout(res, ms));

async function LoadCanvas(grid) {
    await CreateApp(grid[0].length, grid.length)

    CANVAS_LOADED = true

    pixiContainer.classList.remove('hide')
    pixiContainer.classList.add('show')

    app.view.id = "pixi_canvas"
    
    pixiContainer.appendChild(app.view);

    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]]
        }
    }

    const sprites = []

    for (let y = 0; y < grid.length; y++) {
        for (let x = 0; x < grid[0].length; x++) {
            const sprite = new PIXI.Sprite(GetTexture(grid[y][x]));
            
            sprite.x = x * 16;
            sprite.y = y * 16;
            sprite.width = 16;
            sprite.height = 16;
            
            sprites.push(sprite)
        }
    }

    shuffle(sprites)
    let i = 0;

    for (const sprite of sprites) {
        app.stage.addChild(sprite)
    
        if (i % 15 == 0)
            await delay(1)

        i += 1;
    }
}

window.addEventListener('keydown', async (event) => {
    if (event.code !== 'Space')
        return

    event.preventDefault()

    if (CANVAS_LOADED)
        await DestroyCanvas()

    let grid = await eel.generate()()

    console.log('result', grid)

    await LoadCanvas(grid)
})

LoadTextures()
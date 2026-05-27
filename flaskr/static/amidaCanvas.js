/* あみだくじキャンバスの制御 */

// const amidaMap

const MAP_COLOR = 'black';
const MAP_LINE_WIDTH = 1;
const ROUTE_COLOR = 'red';
const ROUTE_LINE_WIDTH= 5;

const DELAY = 2000; // 循環表示待機時間

const EMPTY = 0, RIGHT = 1, LEFT = -1;

let stopLoop = false;

const canvasContainer = document.getElementById('canvasContainer');
const arrowsDiv = document.getElementById('arrowsDiv');
const itemsDiv = document.getElementById('itemsDiv');

const arrowBtns = document.querySelectorAll(".arrowBtn");

const amidaCanvas = document.getElementById('amidaCanvas');
const routeCanvas = document.getElementById('routeCanvas');

const amidaCtx = amidaCanvas.getContext('2d');
const routeCtx = routeCanvas.getContext('2d');

const mapX = amidaMap.length;
const mapY = amidaMap[0].length;

let canvasW, canvasH, spacingX, spacingY;

// 画面サイズの初期化
function init() {
    const rect = canvasContainer.getBoundingClientRect();
    canvasW = rect.width;
    canvasH = rect.height;

    spacingX = canvasW / (mapX + 1);
    spacingY = (mapY != 1) ? canvasH / mapY : canvasH / 20;

    amidaCanvas.width  = canvasW;
    amidaCanvas.height = canvasH;
    routeCanvas.width  = canvasW;
    routeCanvas.height = canvasH;

    document.querySelectorAll('.arrowSpan').forEach(child => {
        child.style.width = spacingX + 'px';
    });

    document.querySelectorAll('.itemSpan').forEach(child => {
        child.style.width = spacingX + 'px';
    });

    showMap();
}
init();

// 画面に合わせて直線を描く
function drawLine(ctx, x1, y1, x2, y2) {
    ctx.beginPath();
    ctx.moveTo((x1 + 1) * spacingX, y1 * spacingY);
    ctx.lineTo((x2 + 1) * spacingX, y2 * spacingY);
    ctx.stroke();
}

// マップ表示
function showMap() {
    clearRoute();

    amidaCtx.strokeStyle = MAP_COLOR;
    amidaCtx.lineWidth = MAP_LINE_WIDTH;

    // 未開封時、option_hide_items オンの場合は枠だけ表示
    if (mapY == 1) {
        for (let x = 0; x < mapX; x++) {
            drawLine(amidaCtx, x, 0, x, 1);
            drawLine(amidaCtx, x, 19, x, 20);
        }
        amidaCtx.strokeRect(0 , spacingY, (mapX + 1) * spacingX, 18 * spacingY);
        return;
    }

    for (let x = 0; x < mapX; x++) {
        drawLine(amidaCtx, x, 0, x, mapY);
        for (let y = 0; y < mapY - 1; y++) {
            if (amidaMap[x][y] == RIGHT) {
                drawLine(amidaCtx, x, y + 1, x + 1, y + 1);
            }
        }
    }
}

// ルート表示
function showRoute(lineNo) {
    routeCtx.strokeStyle = ROUTE_COLOR;
    routeCtx.lineWidth = ROUTE_LINE_WIDTH;
    
    clearRoute();

    arrowBtns[lineNo].style.color = "red";

    let currentX = lineNo;
    for (let y = 0; y < mapY; y++) {
        drawLine(routeCtx, currentX, y, currentX, y + 1);
        if (amidaMap[currentX][y] == RIGHT) {
            const nextX = currentX + 1;
            drawLine(routeCtx, currentX, y + 1, nextX, y + 1);
            currentX = nextX;
        } else if (amidaMap[currentX][y] == LEFT) {
            const nextX = currentX - 1;
            drawLine(routeCtx, currentX, y + 1, nextX, y + 1);
            currentX = nextX;
        }
    }
}

// ルートを消す
function clearRoute() {
    arrowBtns.forEach((btn) => { btn.style.color = "black"; });
    routeCtx.clearRect(0, 0, canvasW, canvasH);
}

// ルート表示を停止する
function hideRoute() {
    stopLoop = true;
    clearRoute();
}

// ルートの表示ループ
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
async function showRouteLoop() {
    stopLoop = false;

    while(!stopLoop) {
        for (let line = 0; line < mapX; line++) {
            clearRoute();
            if (stopLoop) break;

            showRoute(line);
            await sleep(DELAY);
        }
    }
}

// ルート表示ループを停止する
function stopShowRouteLoop() {
    stopLoop = true;
    clearRoute();
}

// 画面サイズが変更される時の再初期化登録
window.addEventListener('resize', init);

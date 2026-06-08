/* あみだくじキャンバスの制御 */

// const amidaMap

const MAP_COLOR = 'black';
const MAP_CIRCLE_COLOR = 'gray';
const MAP_LINE_WIDTH = 1;

const ROUTE_COLOR = 'red';
const ROUTE_LINE_WIDTH= 5;

const RADIUS = 5;

const DELAY = 2000; // 循環表示待機時間

const EMPTY = 0, RIGHT = 1, LEFT = -1;

const startShowRouteLoopBtn = document.getElementById("startShowRouteLoopBtn");
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
        child.style.maxWidth = spacingX + 'px';
    });

    document.querySelectorAll('.itemSpan').forEach(child => {
        child.style.width = spacingX + 'px';
        child.style.maxWidth = spacingX + 'px';
    });

    showMap();
    fitAllTexts();
}

// 文字を合わせてサイズの調整
function fitAllTexts() {
  const boxes = document.querySelectorAll('.responsive-box');

  boxes.forEach(box => {
    const text = box.querySelector('.responsive-text');
    if (!text) return;

    // 初期状態に戻す（折り返しを解除してサイズをリセット）
    text.classList.remove('wrap-text');
    let fontSize = 16;
    text.style.fontSize = fontSize + 'px';

    // ボックスの内側の幅（パディングを除く）を取得
    const maxWidth = box.clientWidth - 2;

    // テキストの幅がボックスの幅より大きい間、1pxずつ小さくする（最小8px）
    while (text.offsetWidth > maxWidth && fontSize > 8) {
      fontSize--;
      text.style.fontSize = fontSize + 'px';
    }

    // 最小サイズ（8px）でも入り切らない場合は、折り返しを許可する
    if (text.offsetWidth > maxWidth) {
      text.classList.add('wrap-text');
    }
  });
}

// 画面に合わせて直線を描く
function drawLine(ctx, x1, y1, x2, y2) {
    ctx.beginPath();
    ctx.moveTo((x1 + 1) * spacingX, y1 * spacingY);
    ctx.lineTo((x2 + 1) * spacingX, y2 * spacingY);
    ctx.stroke();
}

// 画面に合わせて玉を描く
function drawCircle(ctx, x, color) {
    // 下端の玉を描く
    ctx.beginPath();
    ctx.arc((x + 1) * spacingX, canvasH - RADIUS - 1, RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
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

        drawCircle(amidaCtx, x, MAP_CIRCLE_COLOR);
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

    drawCircle(routeCtx, currentX, ROUTE_COLOR);
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
    startShowRouteLoopBtn.disabled = false;
}

// 循環表示開始
function startShowRouteLoop() {
    startShowRouteLoopBtn.disabled = true;
    showRouteLoop();
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

// ページ読み込み時と、画面サイズ変更時に初期化登録
window.addEventListener('DOMContentLoaded', init);
window.addEventListener('resize', init);

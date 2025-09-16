document.addEventListener("DOMContentLoaded", function() {
    //tetris thumbnail functionality
    const tetrisThumbnail = document.getElementById('open-tetris');
    const tetrisGame = document.getElementById('tetris-game');
    
    if (tetrisThumbnail) {
        tetrisThumbnail.addEventListener('click', function() {
            tetrisThumbnail.style.display = 'none';
            tetrisGame.style.display = 'flex';
            initTetris();
        });
    }

    function initTetris() {
        //tetris game implementation
        const canvas = document.getElementById('tetris-canvas');
        const nextCanvas = document.getElementById('next-piece-canvas');
        const ctx = canvas.getContext('2d');
        const nextCtx = nextCanvas.getContext('2d');
        const scoreElement = document.getElementById('score');
        const levelElement = document.getElementById('level');
        const linesElement = document.getElementById('lines');
        const startButton = document.getElementById('start-game');
        const pauseButton = document.getElementById('pause-game');
        
        //game constants
        const ROWS = 20;
        const COLS = 10;
        const BLOCK_SIZE = 30;
        const COLORS = [
            null,
            '#FF0D72', //I
            '#0DC2FF', //J
            '#0DFF72', //L
            '#F538FF', //O
            '#FF8E0D', //S
            '#FFE138', //T
            '#3877FF'  //Z
        ];
        
        //tetromino shapes
        const SHAPES = [
            [],
            [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], // I
            [[2, 0, 0], [2, 2, 2], [0, 0, 0]],                         // J
            [[0, 0, 3], [3, 3, 3], [0, 0, 0]],                         // L
            [[0, 4, 4], [0, 4, 4], [0, 0, 0]],                         // O
            [[0, 5, 5], [5, 5, 0], [0, 0, 0]],                         // S
            [[0, 6, 0], [6, 6, 6], [0, 0, 0]],                         // T
            [[7, 7, 0], [0, 7, 7], [0, 0, 0]]                          // Z
        ];
        
        //game state
        let board = createBoard();
        let piece = null;
        let nextPiece = null;
        let score = 0;
        let level = 1;
        let lines = 0;
        let gameOver = false;
        let paused = false;
        let dropCounter = 0;
        let dropInterval = 800; //faster drop speed
        let lastTime = 0;
        let requestId = null;
        
        //create empty board
        function createBoard() {
            return Array.from({length: ROWS}, () => Array(COLS).fill(0));
        }
        
        //create a new random piece
        function createPiece() {
            const type = Math.floor(Math.random() * 7) + 1;
            return {
                type,
                shape: SHAPES[type],
                x: Math.floor(COLS / 2) - 1,
                y: 0
            };
        }
        
        //draw the board
        function drawBoard() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            //draw the background grid
            for (let y = 0; y < ROWS; y++) {
                for (let x = 0; x < COLS; x++) {
                    ctx.fillStyle = '#222';
                    ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                    ctx.strokeStyle = '#333';
                    ctx.strokeRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                }
            }
            
            //draw the placed pieces
            for (let y = 0; y < ROWS; y++) {
                for (let x = 0; x < COLS; x++) {
                    if (board[y][x]) {
                        ctx.fillStyle = COLORS[board[y][x]];
                        ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                        ctx.strokeStyle = '#000';
                        ctx.strokeRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                    }
                }
            }
            
            //draw the current piece
            if (piece) {
                drawPiece(piece);
            }
        }
        
        //draw a piece
        function drawPiece(piece, ctxToUse = ctx) {
            piece.shape.forEach((row, y) => {
                row.forEach((value, x) => {
                    if (value) {
                        ctxToUse.fillStyle = COLORS[piece.type];
                        ctxToUse.fillRect(
                            (piece.x + x) * BLOCK_SIZE, 
                            (piece.y + y) * BLOCK_SIZE, 
                            BLOCK_SIZE, 
                            BLOCK_SIZE
                        );
                        ctxToUse.strokeStyle = '#000';
                        ctxToUse.strokeRect(
                            (piece.x + x) * BLOCK_SIZE, 
                            (piece.y + y) * BLOCK_SIZE, 
                            BLOCK_SIZE, 
                            BLOCK_SIZE
                        );
                    }
                });
            });
        }
        
        //draw the next piece preview
        function drawNextPiece() {
            nextCtx.clearRect(0, 0, nextCanvas.width, nextCanvas.height);
            
            if (nextPiece) {
                //center the piece in the preview canvas
                const offsetX = (nextCanvas.width / BLOCK_SIZE - nextPiece.shape[0].length) / 2;
                const offsetY = (nextCanvas.height / BLOCK_SIZE - nextPiece.shape.length) / 2;
                
                nextPiece.shape.forEach((row, y) => {
                    row.forEach((value, x) => {
                        if (value) {
                            nextCtx.fillStyle = COLORS[nextPiece.type];
                            nextCtx.fillRect(
                                (offsetX + x) * BLOCK_SIZE, 
                                (offsetY + y) * BLOCK_SIZE, 
                                BLOCK_SIZE, 
                                BLOCK_SIZE
                            );
                            nextCtx.strokeStyle = '#000';
                            nextCtx.strokeRect(
                                (offsetX + x) * BLOCK_SIZE, 
                                (offsetY + y) * BLOCK_SIZE, 
                                BLOCK_SIZE, 
                                BLOCK_SIZE
                            );
                        }
                    });
                });
            }
        }
        
        //check for collisions
        function collide(piece, board) {
            for (let y = 0; y < piece.shape.length; y++) {
                for (let x = 0; x < piece.shape[y].length; x++) {
                    if (piece.shape[y][x] &&
                        (board[piece.y + y] === undefined ||
                         board[piece.y + y][piece.x + x] === undefined ||
                         board[piece.y + y][piece.x + x])) {
                        return true;
                    }
                }
            }
            return false;
        }
        
        //merge the piece with the board
        function merge(piece, board) {
            piece.shape.forEach((row, y) => {
                row.forEach((value, x) => {
                    if (value) {
                        board[piece.y + y][piece.x + x] = value;
                    }
                });
            });
        }
        
        //rotate the piece
        function rotate(piece, direction) {
            const newShape = [];
            for (let y = 0; y < piece.shape[0].length; y++) {
                newShape[y] = [];
                for (let x = 0; x < piece.shape.length; x++) {
                    newShape[y][x] = direction === 1 
                        ? piece.shape[piece.shape.length - 1 - x][y]
                        : piece.shape[x][piece.shape[0].length - 1 - y];
                }
            }
            
            //check if rotation is valid
            const originalShape = piece.shape;
            piece.shape = newShape;
            if (collide(piece, board)) {
                piece.shape = originalShape;
            }
        }
        
        //clear completed lines
        function clearLines() {
            let linesCleared = 0;
            
            outer: for (let y = ROWS - 1; y >= 0; y--) {
                for (let x = 0; x < COLS; x++) {
                    if (board[y][x] === 0) {
                        continue outer;
                    }
                }
                
                //remove the line
                const row = board.splice(y, 1)[0].fill(0);
                board.unshift(row);
                linesCleared++;
                y++; //check the same row again
            }
            
            if (linesCleared > 0) {
                //update score
                lines += linesCleared;
                score += [0, 40, 100, 300, 1200][linesCleared] * level;
                
                //update level every 10 lines
                level = Math.floor(lines / 10) + 1;
                dropInterval = Math.max(100, 800 - (level - 1) * 70); // Faster level progression
                
                //update UI
                scoreElement.textContent = score;
                levelElement.textContent = level;
                linesElement.textContent = lines;
            }
        }
        
        //move the piece
        function movePiece(dir) {
            piece.x += dir;
            if (collide(piece, board)) {
                piece.x -= dir;
            }
        }
        
        //drop the piece
        function dropPiece() {
            piece.y++;
            if (collide(piece, board)) {
                piece.y--;
                merge(piece, board);
                clearLines();
                resetPiece();
                
                //check for game over
                if (collide(piece, board)) {
                    gameOver = true;
                    cancelAnimationFrame(requestId);
                    alert(`Game Over! Your score: ${score}`);
                }
            }
            dropCounter = 0;
        }
        
        //hard drop
        function hardDrop() {
            while (!collide(piece, board)) {
                piece.y++;
            }
            piece.y--;
            dropPiece();
        }
        
        //reset the piece
        function resetPiece() {
            piece = nextPiece || createPiece();
            nextPiece = createPiece();
            drawNextPiece();
        }
        
        //update game state
        function update(time = 0) {
            const deltaTime = time - lastTime;
            lastTime = time;
            
            dropCounter += deltaTime;
            if (dropCounter > dropInterval) {
                dropPiece();
            }
            
            drawBoard();
            
            if (!gameOver && !paused) {
                requestId = requestAnimationFrame(update);
            }
        }
        
        //handle keyboard input
        document.addEventListener('keydown', function(e) {
            if (gameOver || paused) return;
            
            switch (e.keyCode) {
                case 37: //left arrow
                    movePiece(-1);
                    break;
                case 39: //right arrow
                    movePiece(1);
                    break;
                case 40: //down arrow
                    dropPiece();
                    break;
                case 38: //up arrow
                    rotate(piece, 1);
                    break;
                case 32: //space
                    hardDrop();
                    break;
                case 80: //p key
                    togglePause();
                    break;
            }
        });
        
        //start game
        if (startButton) {
            startButton.addEventListener('click', function() {
                if (gameOver) {
                    resetGame();
                }
                
                if (!requestId) {
                    resetGame();
                    requestId = requestAnimationFrame(update);
                    startButton.innerHTML = '<i class="fas fa-redo"></i> Restart';
                }
            });
        }

        //pause game
        if (pauseButton) {
            pauseButton.addEventListener('click', togglePause);
        }    
        
        function togglePause() {
            paused = !paused;
            
            if (paused) {
                cancelAnimationFrame(requestId);
                pauseButton.innerHTML = '<i class="fas fa-play"></i> Resume';
            } else {
                requestId = requestAnimationFrame(update);
                pauseButton.innerHTML = '<i class="fas fa-pause"></i> Pause';
            }
        }
        
        //reset game
        function resetGame() {
            board = createBoard();
            score = 0;
            level = 1;
            lines = 0;
            gameOver = false;
            dropInterval = 800;
            
            scoreElement.textContent = score;
            levelElement.textContent = level;
            linesElement.textContent = lines;
            
            resetPiece();
            drawNextPiece();
        }
        
        //initialize the game
        resetGame();
        drawBoard();
        drawNextPiece();
    }
});

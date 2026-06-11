import streamlit as st
import streamlit.components.v1 as components

# 1. 스트림릿 페이지 기본 설정
st.set_page_config(layout="centered")

st.title("🎮 스트림릿 웹 리듬게임")
st.info("💡 게임 창 안쪽을 마우스로 '클릭'한 뒤, S, D, K, L 키를 누르세요!")

# 2. 에러 방지를 위해 자바스크립트/HTML 코드를 이중 따옴표 규칙에 맞춰 주입
components.html(
    """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 0; background-color: transparent; display: flex; justify-content: center; align-items: center; }
            canvas { background: #1a1a24; display: block; border: 3px solid #4f46e5; border-radius: 8px; }
        </style>
    </head>
    <body>
        <canvas id="gameCanvas" width="500" height="500"></canvas>
        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");
            const lanes = [60, 160, 260, 360];
            const keys = ['s', 'd', 'k', 'l'];
            let keyState = [false, false, false, false];
            let notes = [];
            let score = 0;
            let combo = 0;
            const judgmentLineY = 420;

            window.addEventListener('keydown', (e) => {
                const idx = keys.indexOf(e.key.toLowerCase());
                if (idx !== -1) {
                    if (!keyState[idx]) {
                        keyState[idx] = true;
                        let hit = false;
                        for (let i = 0; i < notes.length; i++) {
                            if (notes[i].lane === idx && Math.abs(notes[i].y - judgmentLineY) < 35) {
                                score += 100 + (combo * 10);
                                combo++;
                                notes.splice(i, 1);
                                hit = true;
                                break;
                            }
                        }
                        if(!hit) combo = 0;
                    }
                }
            });

            window.addEventListener('keyup', (e) => {
                const idx = keys.indexOf(e.key.toLowerCase());
                if (idx !== -1) keyState[idx] = false;
            });

            setInterval(() => {
                if (Math.random() < 0.5) {
                    notes.push({ lane: Math.floor(Math.random() * 4), y: -20, speed: 5 });
                }
            }, 500);

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                for (let i = 0; i < 4; i++) {
                    ctx.fillStyle = keyState[i] ? "rgba(79, 70, 229, 0.2)" : "rgba(255,255,255,0.02)";
                    ctx.fillRect(lanes[i], 0, 80, canvas.height);
                }
                ctx.strokeStyle = "#4f46e5";
                ctx.lineWidth = 4;
                ctx.beginPath(); ctx.moveTo(40, judgmentLineY); ctx.lineTo(460, judgmentLineY); ctx.stroke();

                ctx.fillStyle = "#ff4b4b";
                for (let i = notes.length - 1; i >= 0; i--) {
                    notes[i].y += notes[i].speed;
                    ctx.fillRect(lanes[notes[i].lane] + 5, notes[i].y, 70, 20);
                    if (notes[i].y > canvas.height) { notes.splice(i, 1); combo = 0; }
                }

                ctx.fillStyle = "#ffffff"; ctx.font = "bold 20px Arial"; ctx.fillText("SCORE: " + score, 30, 40);
                if(combo > 0) { ctx.fillStyle = "#ffd700"; ctx.font = "bold 30px Arial"; ctx.fillText(combo + " COMBO", 200, 200); }
                for (let i = 0; i < 4; i++) {
                    ctx.fillStyle = keyState[i] ? "#ffd700" : "#888899";
                    ctx.font = "bold 18px Arial"; ctx.fillText(keys[i].toUpperCase(), lanes[i] + 32, judgmentLineY + 40);
                }
                requestAnimationFrame(draw);
            }
            draw();
        </script>
    </body>
    </html>
    """,
    height=550
)
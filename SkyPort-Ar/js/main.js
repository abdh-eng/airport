
// main.js - سلوكيات عامة (بحث سريع، نماذج، toasts)
$(function(){
  toastr.options = {
    closeButton: true,
    progressBar: true,
    positionClass: 'toast-bottom-left',
    timeOut: 2500
  };

  $('#quick-search-form').on('submit', function(e){
    e.preventDefault();
    const q = $('#quick-search').val().trim();
    if(!q){ toastr.warning('الرجاء إدخال رقم الرحلة أو الوجهة'); return; }
    window.location.href = 'flights.html?search=' + encodeURIComponent(q);
  });

  $('#contact-form').on('submit', function(e){
    e.preventDefault();
    const name = $('#c-name').val().trim(), email = $('#c-email').val().trim(), msg = $('#c-message').val().trim();
    if(!name || !email || !msg){ toastr.error('يرجى تعبئة جميع الحقول'); return; }
    toastr.success('تم إرسال الرسالة. سنعود إليك قريباً.');
    $(this)[0].reset();
  });

  $('#signup-form').on('submit', function(e){
    e.preventDefault();
    const p = $('#signup-password').val(), p2 = $('#signup-password-confirm').val();
    if(p.length < 6){ toastr.error('يجب أن تحتوي كلمة المرور على 6 أحرف على الأقل'); return; }
    if(p !== p2){ toastr.error('كلمتا المرور غير متطابقتين'); return; }
    toastr.success('تم إنشاء الحساب (تجريبي)');
    $(this)[0].reset();
  });

  $('#login-form').on('submit', function(e){
    e.preventDefault();
    const email = $('#login-email').val().trim(), pass = $('#login-password').val();
    if(!email || !pass){ toastr.error('الرجاء إدخال البريد وكلمة المرور'); return; }
    if(email === 'student@example.com' && pass === 'password'){ toastr.success('تم تسجيل الدخول (تجريبي)'); setTimeout(()=> location.href='index.html',800); }
    else toastr.error('بيانات الدخول غير صحيحة (تجريبي)');
  });

  // populate alerts from flights.json (first 3 delayed or boarding)
  $.getJSON('data/flights.json').done(function(data){
    const alertsNode = $('#alerts');
    alertsNode.empty();
    data.slice(0,6).forEach(f=>{
      if(f.status === 'Delayed' || f.status === 'Boarding'){
        const alert = $('<div>').addClass('alert d-flex justify-content-between align-items-center').addClass(f.status==='Delayed'?'alert-warning':'alert-success');
        alert.html('<div><strong>'+f.code+'</strong> إلى '+f.destination+' — '+ (f.status==='Delayed' ? 'مؤخرة' : 'بدء الصعود') +'</div><div><span class="badge '+(f.status==='Delayed'?'bg-danger':'bg-success')+'">'+f.status+'</span></div>');
        alertsNode.append(alert);
      }
    });
  });

});

let navigation = document.querySelector(".navigation");
let close = document.querySelector(".close");
navigation.onclick = function () {
  navigation.classList.add("active");
};
close.onclick = function () {
  navigation.classList.remove("active");
};




// دالة لتغيير حجم الخط بالنسبة المئوية بدقة عالية
function adjustFontSize(percent) {
    const ratio = 1 + percent / 100; // حساب النسبة الدقيقة
    const allElements = document.querySelectorAll('body *'); // كل العناصر داخل البودي

    allElements.forEach(el => {
        const style = window.getComputedStyle(el);
        const currentSize = parseFloat(style.fontSize); // حجم الخط الحالي بالبيكسل

        if (!isNaN(currentSize) && currentSize > 0) {
            // حساب الحجم الجديد بدقة حتى عشرية
            const newSize = +(currentSize * ratio).toFixed(2);
            el.style.fontSize = newSize + 'px';
        }
    });
}




document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginform");

    // إنشاء صفحة التسجيل إذا لم تكن موجودة
    let registerForm = document.getElementById("registerform");
    if (!registerForm) {
        registerForm = document.createElement("div");
        registerForm.id = "registerform";
        registerForm.className = "signin"; 
        registerForm.innerHTML = `
            <div class="content">
                <h2>Signup</h2>
                <div class="form">
                    <div class="inputBox">
                        <input type="text" id="signup-username" required />
                        <i>Username</i>
                    </div>
                    <div class="inputBox">
                        <input type="email" id="signup-email" required />
                        <i>Email</i>
                    </div>
                    <div class="inputBox">
                        <input type="password" id="signup-password" required />
                        <i>Password</i>
                    </div>
                    <div class="inputBox">
                        <input type="submit" value="Create Account" id="signup-btn"/>
                    </div>
                    <div class="links">
                        <a href="#" id="backToLogin">Back to Login</a>
                    </div>
                    <div id="signup-message" style="color:red;margin-top:10px;"></div>
                </div>
            </div>
        `;
        loginForm.parentNode.appendChild(registerForm);
    }

    registerForm.style.display = "none";

    // إظهار صفحة التسجيل
    const showRegisterLink = document.getElementById("showregister");
    showRegisterLink.addEventListener("click", function(e) {
        e.preventDefault();
        loginForm.style.display = "none";
        registerForm.style.display = "block";
    });

    // العودة لتسجيل الدخول
    const backToLoginLink = document.getElementById("backToLogin");
    backToLoginLink.addEventListener("click", function(e) {
        e.preventDefault();
        registerForm.style.display = "none";
        loginForm.style.display = "block";
    });

    // التعامل مع تسجيل الدخول وهميًا
    const loginBtn = loginForm.querySelector('input[type="submit"]');
    loginBtn.addEventListener("click", function(e) {
        e.preventDefault();
        const email = loginForm.querySelector('input[type="text"]').value;
        const password = loginForm.querySelector('input[type="password"]').value;
        const message = loginForm.querySelector("#login-message") || createLoginMessage();

        if (email === "" || password === "") {
            message.style.color = "red";
            message.textContent = "الرجاء ملء جميع الحقول!";
        } else if (email === "user@example.com" && password === "123456") {
            message.style.color = "green";
            message.textContent = "تم الدخول بنجاح!";
        } else {
            message.style.color = "red";
            message.textContent = "البريد أو كلمة المرور خاطئة!";
        }
    });

    function createLoginMessage() {
        const msg = document.createElement("div");
        msg.id = "login-message";
        msg.style.marginTop = "10px";
        loginForm.querySelector(".form").appendChild(msg);
        return msg;
    }

    // التعامل مع إنشاء الحساب وهميًا
    const signupBtn = document.getElementById("signup-btn");
    const signupMessage = document.getElementById("signup-message");
    signupBtn.addEventListener("click", function(e) {
        e.preventDefault();
        const username = document.getElementById("signup-username").value;
        const email = document.getElementById("signup-email").value;
        const password = document.getElementById("signup-password").value;

        if (!username || !email || !password) {
            signupMessage.style.color = "red";
            signupMessage.textContent = "الرجاء ملء جميع الحقول!";
        } else {
            signupMessage.style.color = "green";
            signupMessage.textContent = "تم إنشاء الحساب بنجاح!";
        }
    });
});


const amidaForm          = document.querySelector("form");
const formElements       = document.querySelectorAll("input, select, textarea");

const errorDiv           = document.getElementById("errorDiv");

const titleInput         = document.getElementById("title");
const lineCountInput     = document.getElementById("line_count");
const amidaItemsTextarea = document.getElementById("items");
const optionAORadio      = document.getElementById("option_auto_open");
const optionHIRadio      = document.getElementById("option_hide_items");
const adminPwdInput      = document.getElementById("admin_password");
const adminPwdConfInput  = document.getElementById("admin_password_confirm");
const userPwdInput       = document.getElementById("user_password");
const userPwdConfInput   = document.getElementById("user_password_confirm");

const mode = amidaForm.dataset.mode;

const isASCII = str => /^[\x00-\x7F]*$/.test(str);

function clearError() {
    errorDiv.innerHTML = "";
}

function showError(msg) {
    errorDiv.textContent = msg;
}

function validateLineCount(lineCount) {
    lineCount = parseInt(lineCount, 10);
    return !Number.isNaN(lineCount) && lineCount >= 3 && lineCount <= 20

}

function validatePwd(pwd) {
    return isASCII(pwd) && pwd.length >= 3 && pwd.length <= 20
}

// フォームが送信（submit）される時の処理を登録
function validateAll() {
    clearError();

    // フォーム内容の取得
    const title        = titleInput.value.trim();
    const lineCount    = lineCountInput.value.trim();
    const amidaItems   = amidaItemsTextarea.value.trim();
    const adminPwd     = adminPwdInput.value.trim();
    const adminPwdConf = adminPwdConfInput.value.trim();
    const userPwd      = userPwdInput.value.trim();
    const userPwdConf  = userPwdConfInput.value.trim();

    // 検証：タイトル
    if (!title) {
        showError("タイトルは必ず入力して下さい");
        return false;
    }

    // 検証：本数（作成モードのみ）
    if (mode === "create") {
        if (!lineCount) {
            showError("本数を選択してください");
            return false;
        }
    }

    // 検証：アイテム
    if (!amidaItems) {
        showError("アイテムを入力してください");
        return false;
    }

    // 検証：管理者パスワード
    if (!adminPwd) {
        showError("管理パスワードを入力してください");
        return false;
    } else if (!validatePwd(adminPwd)) {
        showError("管理パスワードは 3 文字以上 20 文字以内で入力してください");
        return false;
    } else if (adminPwd !== adminPwdConf) {
        showError("管理パスワードは、上段と下段で同じものを入力して下さい");
        return false;
    }

    // 検証：利用パスワード（選択）
    if (userPwd) {
        if (!validatePwd(userPwd)) {
            showError("利用パスワードは 3 文字以上 20 文字以内で入力してください");
            return false;
        } else if (userPwd !== userPwdConf) {
            showError("利用パスワードは、上段と下段で同じものを入力して下さい");
            return false;
        }
    }

    return true;
}

formElements.forEach(element => {
    // 文字が入力されるたびにチェックを実行！
    element.addEventListener("input", () => {
        validateAll();
    });
});

amidaForm.addEventListener("submit", (event) => {
    // エラーがあったら送信止め
    if (!validateAll()) {
        event.preventDefault();
    }
});

function toggleFields() {
    // 本数正しい入力されなければ、下の枠を入力不可にする
    const lineCount = lineCountInput.value.trim();
    if (validateLineCount(lineCount)) {
        amidaItemsTextarea.disabled = false;
        optionAORadio.disabled = false;
        optionHIRadio.disabled = false;
        adminPwdInput.disabled = false;
        adminPwdConfInput.disabled = false;
        userPwdInput.disabled = false;
        userPwdConfInput.disabled = false;
    } else {
        amidaItemsTextarea.disabled = true;
        optionAORadio.disabled = true;
        optionHIRadio.disabled = true;
        adminPwdInput.disabled = true;
        adminPwdConfInput.disabled = true;
        userPwdInput.disabled = true;
        userPwdConfInput.disabled = true;
    }
}
toggleFields();
lineCountInput.addEventListener("input", toggleFields);

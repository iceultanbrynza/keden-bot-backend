document.addEventListener("DOMContentLoaded", () => {
    const tg = window.Telegram.WebApp;
    if (!tg) {
        console.warn("Not in Telegram WebView");
        return;
    }
    tg.ready();

    const textareas = document.querySelectorAll('textarea.auto-resize');
    textareas.forEach(textarea => {
        textarea.style.height = textarea.scrollHeight + 'px';

        document.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        });
    });


    const form = document.getElementById("user-form");
    const submitButton = form.querySelector("button[type=submit]");
    const loader = document.getElementById("loader-overlay");
    const module_id = window.appData?.module_id;
    const role = window.appData?.role;
    let url;
    const MAX_SIZE = 50 * 1024 * 1024;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        if(await isFormEmpty(formData)){
            alert('Заполните поля, чтобы мы могли понять Вашу проблему');
            return;
        }

        loader.style.display = "flex";
        submitButton.disabled = true;         // отключаем кнопку
        submitButton.textContent = "Подождите, пожалуйста";

        const contact_id = await getContact();
        const user_id = tg.initDataUnsafe.user?.id;
        const user_name = tg.initDataUnsafe.user?.username;

        let resultText = "";

        for (const [key, value] of formData.entries()) {
            resultText += `${key}: ${value}\n`;
        }

        let data = {
            entityTypeId: 1444,
            fields:{
                ufCrm168Text: resultText,
                ufCrm168FioFromTg: user_name,
                ufCrm168UserChatId: user_id,
                contactId: contact_id
            }
        };

        if(module_id!=undefined) {
            data.fields.ufCrm168SelectModule = module_id;
        }

        const fileInputs = [
            {
                id: "screen",
                prefix: "screen",
                restrection: 5,
                extenstion: "png"
            },
            {
                id: "video",
                prefix: "video",
                restrection: 1,
                extenstion: "mp4"
            },
            {
                id: "screen-variable",
                prefix: "screen-var",
                restrection: 2,
                extenstion: "png"
            },
            {
                id: "video-variable",
                prefix: "video-var",
                restrection: 1,
                extenstion: "mp4"
            },
            {
                id: "doc",
                prefix: "doc",
                restrection: 1,
                extenstion: "pdf"
            }
        ];

        data.fields.ufCrm168Files = [];
        let overall_size = 0;

        for(const fileInput of fileInputs){
            const input = document.getElementById(fileInput.id);
            if (!input || !input.files) continue;
            if(input.files.length>fileInput.restrection){
                alert(`Можно загрузить не более ${fileInput.restrection} файлов`);
                input.value = ''; // сбрасываем выбор
                loader.style.display = "none";
                submitButton.disabled = false;
                submitButton.textContent = "Сохранить";
                return;
            }

            if(input.files && input.files.length > 0){
                for(const file of input.files){
                    overall_size += file.size;
                    if(overall_size > MAX_SIZE){
                        alert(`Можно загрузить не более ${MAX_SIZE} файлов`);
                        input.value = ''; // сбрасываем выбор
                        loader.style.display = "none";
                        submitButton.disabled = false;
                        submitButton.textContent = "Сохранить";
                        return;
                    }
                    const base64 = await fileToBase64(file);
                    const filename = await generateFilename(fileInput.prefix, fileInput.extenstion);
                    data.fields.ufCrm168Files.push([filename, base64]);
                }
            }

        }
        if(role == 'uved') {
            url = "https://keden-bot-backend.onrender.com/kedenbot/uved"
        } else{
            url = "https://keden-bot-backend.onrender.com/kedenbot/udl"
        }
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(data)
            });

        } catch (error) {
            console.error("Error:", error);
        }

        tg.close()
    });
    async function getContact(){
        const user_id = tg.initDataUnsafe.user?.id;
        const url = new URL("https://keden-bot-backend.onrender.com/kedenbot/contactid");
        url.searchParams.set("UF_CRM_CHAT_ID", user_id);

        try {
            const response = await fetch(url, {
                method: "GET",
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();
            if(Array.isArray(result.result)){
                contact = result.result[0];
            } else{
                contact = result.result;
            }
            return contact.ID;
        } catch (error) {
            console.error("Error:", error);
        }
    };
    async function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    };
    async function generateFilename(prefix = "file", extension = "png") {
        const now = new Date();
        const y = now.getFullYear();
        const m = String(now.getMonth() + 1).padStart(2, '0');
        const d = String(now.getDate()).padStart(2, '0');
        const h = String(now.getHours()).padStart(2, '0');
        const min = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        return `${prefix}_${y}${m}${d}_${h}${min}${s}.${extension}`;
      };
    async function isFormEmpty(formData){
        for(const [_, value] of formData.entries()){
            if(!(value instanceof File)){
                if(typeof value === 'string' && value.trim() !== ''){
                    return false;
                }
            }
        }
        return true;
    };
});
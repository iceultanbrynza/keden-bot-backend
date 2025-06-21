document.addEventListener("DOMContentLoaded", () => {
    const tg = window.Telegram.WebApp;
    if (!tg) {
        console.warn("Not in Telegram WebView");
        return;
    }
    tg.ready();
    form = document.getElementById("user-form");
    const module_id = window.appData?.module_id;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const contact_id = await getContact();
        const user_id = tg.initDataUnsafe.user?.id;
        const user_name = tg.initDataUnsafe.user?.username;

        const formData = new FormData(form);
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
                restrection: 5
            },
            {
                id: "video",
                prefix: "video",
                restrection: 1
            },
            {
                id: "screen-variable",
                prefix: "screen-var",
                restrection: 2
            },
            {
                id: "video-variable",
                prefix: "video-var",
                restrection: 1
            },
            {
                id: "doc",
                prefix: "doc",
                restrection: 1
            }
        ];

        data.fields.ufCrm168Files = [];

        for(const fileInput of fileInputs){
            const input = document.getElementById(fileInput.id);
            if (!input || !input.files) continue;
            if(input.files.length>fileInput.restrection){
                alert(`Можно загрузить не более ${fileInput.restrection} файлов`);
                input.value = ''; // сбрасываем выбор
                return;
            }

            if(input.files && input.files.length > 0){
                for(const file of input.files){
                    const base64 = await fileToBase64(file);
                    const filename = generateFilename('screen', 'png');
                    data.fields.ufCrm168Files.push([filename, base64]);
                }
            }

        }

        const url = "https://keden-bot-backend.onrender.com/kedenbot/uved"
        try {
            const response = await fetch(url, {
                method: "POST",
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
    }
    function generateFilename(prefix = "file", extension = "png") {
        const now = new Date();
        const y = now.getFullYear();
        const m = String(now.getMonth() + 1).padStart(2, '0');
        const d = String(now.getDate()).padStart(2, '0');
        const h = String(now.getHours()).padStart(2, '0');
        const min = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        return `${prefix}_${y}${m}${d}_${h}${min}${s}.${extension}`;
      }
});
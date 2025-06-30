function auto_resize(textarea){
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 3 + 'px' ;
};

document.addEventListener("DOMContentLoaded", ()=>{
    const tg = window.Telegram.WebApp;
    const form = document.getElementById('user-form')
    tg.ready();
    const textareas = document.querySelectorAll('textarea.auto-resize');
    textareas.forEach(textarea => {
        auto_resize(textarea);
    });

    form.addEventListener("submit", async function(event){
        event.preventDefault();

        const user_id = tg.initDataUnsafe.user?.id;
        const urls = JSON.parse(document.getElementById('urls-data').textContent);
        alert(urls);
        if (!Array.isArray(urls) || urls.length === 0) {
            alert("Нет файлов для отправки");
            return;
        }
        const url = `https://keden-bot-backend.onrender.com/kedenbot/get_appl?chat_id=${user_id}`;
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(urls)
            });

        } catch (error) {
            alert('Мы не смогли сделать запрос на отправку Ваших файлов. Попробуйте еще раз.')
        }
        tg.close();
    });
});
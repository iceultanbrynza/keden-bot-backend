document.addEventListener("DOMContentLoaded", () => {
  const tg = window.Telegram.WebApp;
  tg.ready();
  // if (!tg || !tg.initDataUnsafe?.user?.id) {
  //   alert("Откройте WebApp из Telegram");
  // }
  let contactId;
  const mode = window.appData.mode;
  const form = document.getElementById("user-form");

  async function getContact(){
    const user_id = tg.initDataUnsafe.user?.id;
    const url = new URL("https://keden-bot-backend.onrender.com/kedenbot/contactid");
    url.searchParams.set("UF_CRM_CHAT_ID", user_id);

    try {
      const response = await fetch(url, {
        method: "GET",
      });

      const result = await response.json();
      console.log(result);
      return result;
    } catch (error) {
      console.error("Error:", error);
    }
  };

  if(mode === 'edit'){
    (async () => {
      const result = await getContact();
      if (!result || !result.result || result.result.length === 0) {
        console.log("Контакт не найден");
        return;
      }
      console.log(result);
      let contact;
      if(Array.isArray(result.result)){
        contact = result.result[0];
      } else{
        contact = result.result;
      }
      contactId = contact.ID
      document.getElementById("lastName").value = contact.LAST_NAME || '';
      document.getElementById("firstName").value = contact.NAME || '';
      document.getElementById("middleName").value = contact.SECOND_NAME || '';
      document.getElementById("phone").value = contact.PHONE?.[0]?.VALUE || '';
      document.getElementById("email").value = contact.EMAIL?.[0]?.VALUE || '';
    })();
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const user_id = tg.initDataUnsafe.user?.id;
    
    let data = {
      FIELDS:{
          LAST_NAME: form.lastName.value,
          NAME: form.firstName.value,
          SECOND_NAME: form.middleName.value,
          PHONE: [
            {
              VALUE: form.phone.value,
              VALUE_TYPE: "WORK"
            }
          ],
          EMAIL: [
            {
              VALUE: form.email.value,
              VALUE_TYPE: "MAILING"
            }
          ],
          UF_CRM_CHAT_ID: user_id
      }
    };

    if(mode === 'edit'){
      data.ID = contactId;
      try {
        const response = await fetch("https://keden-bot-backend.onrender.com/kedenbot/register?mode=edit", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
        });


        const result = await response.json();
        console.log("Server response:", result);
      } catch (error) {
        console.error("Error:", error);
      }
    } else {
      try {
        const response = await fetch("https://keden-bot-backend.onrender.com/kedenbot/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
        });


        const result = await response.json();
        console.log("Server response:", result);
      } catch (error) {
        console.error("Error:", error);
      }
    }
    tg.close(); // закрыть WebApp
    });
});
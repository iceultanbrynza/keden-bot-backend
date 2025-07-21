document.addEventListener("DOMContentLoaded", () => {
  const tg = window.Telegram.WebApp;
  tg.ready();
  let contactId;
  const mode = window.appData.mode;
  const form = document.getElementById("user-form");
  const URL_BASE = window.appData?.django_url;

  if (mode === 'edit') {
    (async () => {
      const result = await getContact();
      if (!result || !result.result || result.result.length === 0) {
        alert('Вы не зарегистрированы!')
        return;
      }
      let contact;
      if (Array.isArray(result.result)) {
        contact = result.result[0];
      } else {
        contact = result.result;
      }
      contactId = contact.ID
      document.getElementById("lastName").value = contact.LAST_NAME || '';
      document.getElementById("firstName").value = contact.NAME || '';
      document.getElementById("middleName").value = contact.SECOND_NAME || '';
      document.getElementById("phone").value = contact.PHONE?.[0]?.VALUE || '+7';
      document.getElementById("email").value = contact.EMAIL?.[0]?.VALUE || '';
    })();
  } else {
    (async () => {
      const result = await getContact();
      if (result.result && result.result.length > 0) {
        alert('Вы уже зарегистрированы! Попробуйте наши функции')
        tg.close()
        return;
      }
    })();
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const user_id = tg.initDataUnsafe.user?.id;

    if (!isLengthValid(form)) {
      alert('Неправильный ввод: слишком мало/много символов');
      return;
    }

    let data = {
      FIELDS: {
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

    console.log(mode)
    if (mode === 'edit') {
      data.ID = contactId;
      try {
        const response = await fetch(`${URL_BASE}/kedenbot/register_user?mode=edit`, {
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
        const response = await fetch(`${URL_BASE}/kedenbot/register_user`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
        });
        const result = await response.json();
      } catch (error) {
        console.error("Error:", error);
      }
    }
    tg.close(); // закрыть WebApp
  });

  async function getContact() {
    const user_id = tg.initDataUnsafe.user?.id;
    const url = new URL(`${URL_BASE}/kedenbot/contactid`);
    url.searchParams.set("UF_CRM_CHAT_ID", user_id);

    try {
      const response = await fetch(url, {
        method: "GET",
      });

      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Error:", error);
    }
  };

  function isLengthValid(form) {
    return (form.lastName.value.length <= 50 &&
      form.firstName.value.length <= 50 &&
      form.middleName.value.length <= 50 &&
      form.phone.value.length <= 12 &&
      form.phone.value.length >= 10 &&
      form.email.value.length <= 100
    );
  };
});
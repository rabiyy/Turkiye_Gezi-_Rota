// 1. Para birimi formatlama fonksiyonu 
function formatCurrency(value) {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0
  }).format(value);
}

// 2. Mesajları ekrana basma fonksiyonu (Kullanıcı mesajları için)
function appendMessage(container, role, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// 3. Tema (Dark/Light Mode) Ayarları
function initTheme() {
  const button = document.getElementById("themeToggle");
  if (!button) return;

  const saved = localStorage.getItem("theme");
  if (saved === "dark") {
    document.body.classList.add("dark");
  }

  button.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    const theme = document.body.classList.contains("dark") ? "dark" : "light";
    localStorage.setItem("theme", theme);
  });
}

// 4. Adresleri Google Maps linkine çeviren fonksiyon
function linkifyAddresses(text) {
  const addressRegex = /((?:\*\*?)?(?:Adresi?|Konumu?)(?:\*\*?)?)\s*:\s*(.+)/gi;
  
  return text.replace(addressRegex, (match, label, address) => {
    const cleanAddress = address.replace(/\.$/, '').trim();
    const encodedAddress = encodeURIComponent(cleanAddress);
    const mapLink = `https://maps.google.com/?q=$${encodedAddress}`;
    
    return `${match} <br><a href="${mapLink}" target="_blank" style="display:inline-block; margin-top:8px; margin-bottom:8px; padding:6px 12px; background-color:#4285F4; color:white; text-decoration:none; border-radius:5px; font-size:0.9em; font-weight:bold;">📍 Haritada Göster</a>`;
  });
}

// 5. Metni Düzenleyen Sadeleştirilmiş Fonksiyon 
function formatResponseText(text) {
  // Sadece harita linklerini oluştur ve satır sonlarını <br>'e çevir
  let formattedText = linkifyAddresses(text);
  return formattedText.replace(/\n/g, '<br>');
}

// 6. Ana Chat Fonksiyonu
function initChat() {
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const chatWindow = document.getElementById("chatWindow");
  if (!form || !input || !chatWindow) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendMessage(chatWindow, "user", message);
    input.value = "";

    const loadingBubble = document.createElement("div");
    loadingBubble.className = "bubble assistant";
    loadingBubble.innerHTML = "<i>Asistanım rotayı analiz ediyor...</i>";
    chatWindow.appendChild(loadingBubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
      });
      const data = await response.json();
      chatWindow.removeChild(loadingBubble);
      
      const formattedResponse = formatResponseText(data.response);
      const botBubble = document.createElement("div");
      botBubble.className = "bubble assistant";
      botBubble.innerHTML = formattedResponse;
      chatWindow.appendChild(botBubble);

    } catch (error) {
      loadingBubble.innerHTML = "⚠️ Sunucuya bağlanılamadı.";
    }
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });
}

// 7. Navbar Kategori Tıklama Fonksiyonu
function initNavbarCategories() {
  const categoryLinks = document.querySelectorAll(".dropdown-content a");
  const chatWindow = document.getElementById("chatWindow");
  if (!categoryLinks || !chatWindow) return;

  categoryLinks.forEach(link => {
    link.addEventListener("click", async (e) => {
      e.preventDefault();
      const kategoriAdi = link.innerText.trim();

      appendMessage(chatWindow, "user", `${kategoriAdi} kategorisini listele.`);

      const loadingBubble = document.createElement("div");
      loadingBubble.className = "bubble assistant";
      loadingBubble.innerHTML = `<i>${kategoriAdi} için veriler getiriliyor...</i>`;
      chatWindow.appendChild(loadingBubble);
      chatWindow.scrollTop = chatWindow.scrollHeight;

      try {
        const response = await fetch(`http://127.0.0.1:5000/api/yerler?kategori=${encodeURIComponent(kategoriAdi)}`);
        const data = await response.json();

        chatWindow.removeChild(loadingBubble);

        if (!data.results || data.results.length === 0) {
          appendMessage(chatWindow, "assistant", `Maalesef bu kategoride henüz bir kayıt bulunmuyor.`);
          return;
        }

        let responseText = `${kategoriAdi} kategorisinde bulduğum yerler:\n\n`;
        data.results.forEach(yer => {
          responseText += `**${yer.name}**\nKonumu: ${yer.city}\n\n`;
        });

        const formattedResponse = formatResponseText(responseText);

        const botBubble = document.createElement("div");
        botBubble.className = "bubble assistant";
        botBubble.innerHTML = formattedResponse;
        chatWindow.appendChild(botBubble);

      } catch (error) {
        loadingBubble.innerHTML = "⚠️ Veri çekilirken bir hata oluştu.";
      }
      chatWindow.scrollTop = chatWindow.scrollHeight;
    });
  });
}

// Tüm fonksiyonları çalıştır
initTheme();
initChat();
initNavbarCategories();
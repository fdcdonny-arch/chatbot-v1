# ============================================================
#  💬 Asisten IT Chatbot dengan Dukungan Suara (STT + TTS + Cursor Blink)
#  Dibuat oleh Donny Fir | Streamlit + Gemini + gTTS
# ============================================================

# --- 1. Import Library ---
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_mic_recorder import mic_recorder
import tempfile
import speech_recognition as sr
from gtts import gTTS
import os
import time
import json

# --- 2. Konfigurasi Halaman ---
st.set_page_config(page_title="Asisten IT Chatbot", page_icon="💬")
st.markdown(
    """
    <style>
    body { animation: fadeIn 0.8s ease-in; }
    @keyframes fadeIn { from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: translateY(0);} }
    .blinking-cursor {
        font-weight: bold;
        font-size: 1.1em;
        color: #4A90E2;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("💬 Asisten IT - Chatbot")
st.caption("Selamat datang di Asisten IT — Kami siap membantu Anda!")

# File tempat menyimpan riwayat chat
CHAT_HISTORY_FILE = os.path.join(tempfile.gettempdir(), "chat_history.json")

# --- 3. Fungsi Simpan & Muat Riwayat ---
def save_chat_history(messages):
    """Simpan riwayat chat ke file JSON lokal."""
    try:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Gagal menyimpan riwayat chat: {e}")

def load_chat_history():
    """Muat riwayat chat dari file JSON jika tersedia."""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Gagal memuat riwayat chat: {e}")
    return []

# --- 4. Sidebar Pengaturan ---
with st.sidebar:
    st.subheader("⚙️ Pengaturan")

    google_api_key = st.secrets["GOOGLE_API_KEY"]

    temperature = st.slider("Tingkat Kreativitas", 0.0, 2.0, 0.5, 0.05, help="Nilai yang lebih tinggi membuat respons lebih kreatif dan kurang dapat diprediksi.")
    thinking_enabled = st.toggle("Aktifkan Mode Berpikir", value=True, help="Mode berpikir menggunakan parameter 'thinkingBudget' untuk meningkatkan penalaran dalam model tertentu. Menonaktifkannya dapat mengurangi latensi.")
    max_output_tokens = st.number_input("Token Output Maksimum", 1, 4096, 1024, 1, help="Setel token output maksimum yang diinginkan di sini")
    reset_button = st.button("🔄 Reset Percakapan", use_container_width=True, help="Hapus semua pesan dan mulai baru")

    # --- Tombol Simpan & Muat Riwayat ---
    st.markdown("---")
    st.subheader("💾 Manajemen Riwayat")

    save_history_button = st.button("💾 Simpan Riwayat", use_container_width=True)
    load_history_button = st.button("📂 Muat Riwayat", use_container_width=True)

    if save_history_button:
        try:
            save_chat_history(st.session_state.get("messages", []))
            st.success("✅ Riwayat percakapan berhasil disimpan ke file lokal.")
        except Exception as e:
            st.error(f"Gagal menyimpan riwayat: {e}")

    if load_history_button:
        try:
            st.session_state.messages = load_chat_history()
            st.success("📂 Riwayat percakapan berhasil dimuat.")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal memuat riwayat: {e}")


# --- 5. Reset Percakapan ---
if reset_button:
    for key in ["agent", "messages", "voice_text", "audio"]:
        st.session_state.pop(key, None)
    if os.path.exists(CHAT_HISTORY_FILE):
        os.remove(CHAT_HISTORY_FILE)
    st.rerun()


# --- 6. Validasi API Key ---
if not google_api_key:
    st.info("🗝️ Tambahkan API Key Anda untuk memulai percakapan.", icon="🔐")
    st.stop()

# --- 7. Inisialisasi Agent ---
if ("agent" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=temperature,
            thinking_enabled=thinking_enabled,
            max_output_tokens=max_output_tokens
        )
        st.session_state.agent = create_react_agent(
            model=llm,
            tools=[],
            prompt=(
                "Anda adalah seorang ahli yang hanya menjawab pertanyaan tentang Jaringan & CCTV. "
                "Berikan solusi teknis yang sopan dan informatif. "
                "Jika pertanyaan di luar topik, balas dengan: "
                "'Maaf, saya hanya bisa menjawab pertanyaan seputar Jaringan & CCTV. "
                "Apakah ada yang ingin Anda tanyakan tentang hal itu?'"
            )
        )
        st.session_state._last_key = google_api_key
        st.session_state.pop("messages", None)
    except Exception as e:
        st.error(f"Terjadi kesalahan konfigurasi API: {e}")
        st.stop()

# --- 8. Inisialisasi Riwayat Pesan ---
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# --- 9. Tampilkan Riwayat Pesan Lama ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 10. Input Suara / Teks ---
st.markdown("Gunakan suara atau ketik pertanyaan Anda:")

audio = mic_recorder(start_prompt="Mulai Rekam 🎤", stop_prompt="Berhenti Rekam ⏹️", just_once=True, use_container_width=True, format="wav")
voice_text = ""

if audio is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio["bytes"])
        tmp_path = tmp.name
    recognizer = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_data = recognizer.record(source)
        try:
            voice_text = recognizer.recognize_google(audio_data, language="id-ID")
            st.success(f"🎧 Hasil transkripsi suara: **{voice_text}**")
        except sr.UnknownValueError:
            st.warning("⚠️ Tidak dapat mengenali suara.")
        except sr.RequestError:
            st.error("🚫 Gagal menghubungkan ke layanan pengenalan suara.")

prompt = voice_text if voice_text else st.chat_input("Apa yang ingin Anda tanyakan...")

# --- 11. Pemrosesan Chat ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        with st.chat_message("assistant"):
            with st.spinner("💭 Asisten sedang berpikir..."):
                response = st.session_state.agent.invoke({"messages": messages})

            answer = response.get("messages", [])
            if answer:
                answer = answer[-1].content
            else:
                answer = "Maaf, saya tidak dapat menghasilkan respons."

            # === ✨ Efek Mengetik + Cursor Berkedip ===
            placeholder = st.empty()
            displayed_text = ""
            cursor_html = '<span class="blinking-cursor">█</span>'
            for char in answer:
                displayed_text += char
                placeholder.markdown(displayed_text + cursor_html, unsafe_allow_html=True)
                delay = 0.005 if len(answer) > 500 else 0.015
                time.sleep(delay)
            placeholder.markdown(displayed_text, unsafe_allow_html=True)

            # === 🎧 Text-to-Speech (AI Bicara) ===
            try:
                tts = gTTS(text=answer, lang="id")
                tts_path = os.path.join(tempfile.gettempdir(), "ai_voice.mp3")
                tts.save(tts_path)
                st.audio(tts_path, format="audio/mp3")
            except Exception as e:
                st.warning(f"🔇 Gagal memutar suara balasan: {e}")

        st.session_state.messages.append({"role": "assistant", "content": answer})

        # 💾 Simpan otomatis setiap kali ada balasan baru
        save_chat_history(st.session_state.messages)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses permintaan: {e}")

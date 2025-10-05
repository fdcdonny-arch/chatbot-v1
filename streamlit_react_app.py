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

# --- 3. Sidebar Pengaturan ---
with st.sidebar:
    st.subheader("⚙️ Pengaturan")

    google_api_key = st.secrets["GOOGLE_API_KEY"]

    temperature = st.slider("Tingkat Kreativitas", 0.0, 2.0, 0.5, 0.05)
    thinking_enabled = st.toggle("Aktifkan Mode Berpikir", value=True)
    max_output_tokens = st.number_input("Token Output Maksimum", 1, 4096, 1024, 1)
    reset_button = st.button("🔄 Reset Percakapan", help="Hapus semua pesan dan mulai baru")

# --- 4. Reset Percakapan ---
if reset_button:
    # If the reset button is clicked, clear the agent and message history from memory.
    st.session_state.pop("agent", None)
    st.session_state.pop("messages", None)
    # st.rerun() tells Streamlit to refresh the page from the top.
    st.rerun()

# --- 5. Validasi API Key ---
if not google_api_key:
    st.info("🗝️ Tambahkan API Key Anda untuk memulai percakapan.", icon="🔐")
    st.stop()

# --- 6. Inisialisasi Agent ---
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

# --- 7. Inisialisasi Riwayat Pesan ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 8. Tampilkan Riwayat Pesan Lama ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 9. Input Suara / Teks ---
st.markdown("### 🎙️ Gunakan suara atau ketik pertanyaan Anda:")

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

prompt = st.chat_input("Apa yang ingin Anda tanyakan...") or voice_text

# --- 10A. Deteksi Permintaan Jawaban Singkat ---
short_request_keywords = [
    "singkat", "ringkas", "cepat", "to the point",
    "secukupnya", "pendek", "nggak usah panjang", "jawaban aja"
]

is_short_answer = any(keyword in prompt.lower() for keyword in short_request_keywords)


# --- 10B. Pemrosesan Chat ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Siapkan riwayat percakapan untuk model
        messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Tambahkan konteks tambahan berdasarkan mode jawaban
        extra_instruction = (
            "Jawablah secara **singkat dan padat**, tanpa penjelasan tambahan."
            if is_short_answer
            else "Berikan penjelasan yang lengkap dan mudah dipahami."
        )

        # Masukkan instruksi tambahan ke pesan terakhir
        messages.append(
            HumanMessage(content=f"{prompt}\n\nInstruksi tambahan: {extra_instruction}")
        )

        with st.chat_message("assistant"):
            with st.spinner("💭 Asisten sedang berpikir..."):
                response = st.session_state.agent.invoke({"messages": messages})

            # Ambil hasil jawaban model
            if "messages" in response and len(response["messages"]) > 0:
                answer = response["messages"][-1].content
            else:
                answer = "Maaf, saya tidak dapat menghasilkan respons."

            # === ✨ Efek Mengetik + Cursor Berkedip ===
            placeholder = st.empty()
            displayed_text = ""
            cursor_html = '<span class="blinking-cursor">█</span>'
            for char in answer:
                displayed_text += char
                placeholder.markdown(displayed_text + cursor_html, unsafe_allow_html=True)
                time.sleep(0.015)
            placeholder.markdown(displayed_text, unsafe_allow_html=True)

            # === 🎧 Text-to-Speech (AI Bicara) ===
            try:
                tts = gTTS(text=answer, lang="id")
                tts_path = os.path.join(tempfile.gettempdir(), "ai_voice.mp3")
                tts.save(tts_path)
                st.audio(tts_path, format="audio/mp3")
            except Exception as e:
                st.warning(f"🔇 Gagal memutar suara balasan: {e}")

        # Simpan ke riwayat percakapan
        st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses permintaan: {e}")


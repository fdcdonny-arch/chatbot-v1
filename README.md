# 🤖 Asisten IT chatbot-v1

Asisten IT Chatbot adalah aplikasi chatbot berbasis **Python** dan **Streamlit** yang dapat membantu menjawab pertanyaan seputar IT, troubleshooting, serta memberikan rekomendasi solusi secara interaktif.


## 🚀 Fitur Utama
- Chatbot interaktif berbasis web dengan **Streamlit**  
- Integrasi dengan **LLM / NLP model** untuk memahami pertanyaan pengguna  
- Respon otomatis terkait troubleshooting IT (jaringan & CCTV)  
- Antarmuka sederhana dan mudah digunakan  
- Mudah di-deploy ke **Streamlit Cloud**, **Heroku**, atau **VPS**  


## 🛠️ Teknologi yang Digunakan
- [Python 3.9+](https://www.python.org/)  
- [Streamlit](https://streamlit.io/)  
- [LangChain](https://www.langchain.com/) *(opsional, jika ingin integrasi dengan LLM)*  
- [GeminiAI API](https://aistudio.google.com/) atau model lain sebagai backend NLP  


## 📂 Struktur Project

asisten-it-chatbot/
│── streamlit_react_app.py # Main aplikasi Streamlit
│── requirements.txt # Daftar dependensi
│── README.md # Dokumentasi project
│── .devcontainer


## ⚙️ Instalasi & Menjalankan
1. Clone repository ini:
   ```bash
   git clone https://github.com/fdcdonny-arch/tes-chatbot-v1.git
   cd tes-chatbot-v1
2. Buat virtual environment (opsional tapi direkomendasikan):
   ```bash
   python -m venv venv
   source venv/bin/activate   # MacOS/Linux
   venv\Scripts\activate      # Windows

4. Install dependencies:
   ```bash
   pip install -r requirements.txt

6. Jalankan aplikasi:
   ```bash
   streamlit run streamlit_react_app.py

8. Buka di browser:
   ```
   http://localhost:8501


📖 Contoh Penggunaan

Menanyakan troubleshooting jaringan:
"Kenapa wifi saya tidak bisa connect?"

Menanyakan hardware error:
"Bagaimana cara memperbaiki CCTV yang rusak?"

Rekomendasi hardware:
"Router Wifi yang bagus apa ya?"


🖼️ Screenshot

<img width="1034" height="785" alt="image" src="https://github.com/user-attachments/assets/5b0eceb7-e02c-4b6b-9f26-edeb7f9f19ea" />



☁️ Deployment

Streamlit Cloud: upload ke GitHub dan hubungkan ke akun Streamlit

Heroku / Render / VPS: jalankan dengan perintah streamlit run streamlit_react_app.py


## 🙌 Dukungan

<p align="center">
  <a href="https://hacktiv8.com" target="_blank">
    <img src="https://res.cloudinary.com/startup-grind/image/upload/c_fill,dpr_2,f_auto,g_center,q_auto:good/v1/gcs/platform-data-goog/events/LOGO%2520Mebiso%2520Horizontal%25202.png" width="200"/>
  </a>
</p>

Project **Asisten IT Chatbot** ini didukung oleh [Hacktiv8](https://hacktiv8.com) sebagai bagian dari program pembelajaran dan pengembangan teknologi.  
Terima kasih kepada para mentor dan rekan peserta yang telah membantu dalam proses pembuatan project ini.

### 👨‍🏫 Mentor
- [Adipta Martulandi](https://www.linkedin.com/in/adiptamartulandi/)


🤝 Kontribusi

Pull request sangat diterima! Jika menemukan bug atau ingin menambahkan fitur baru, silakan buat issue terlebih dahulu.

📜 Lisensi

Project ini menggunakan lisensi MIT – silakan gunakan, modifikasi, dan distribusikan dengan bebas.

# 🎬 AI Talking-Head Studio (D-ID)

A production-grade AI talking-head video generator powered by the **D-ID API** and **Microsoft Azure Speech Synthesis**. Available as both a **Streamlit Web Application** (`app.py`) and a **Next.js 14 Web Application** (`app/page.tsx`).

---

## 🌟 Features

- **Real HTTPS Integration with D-ID API**: Generates real AI presenter videos with lip-syncing.
- **Presenter Avatar**: Specify any direct frontal face JPEG/PNG image URL with dynamic live preview and instant pre-filled default URL for testing.
- **Microsoft Azure Neural Voices**: Choose from multiple natural speech voices (`en-US-JennyNeural`, `en-US-GuyNeural`, `en-US-AriaNeural`, `en-GB-SoniaNeural`, `en-GB-RyanNeural`).
- **Live Studio Monitor**: Real-time polling with progress bar, embedded video player, and one-click MP4 download.
- **Generation History**: Replay and review previous video clips generated in your session.
- **Dual Web App Stack**: Ready to run natively in **Python / Streamlit** or **TypeScript / Next.js**.

---

## 🚀 Quickstart: Streamlit Web App (Python)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the root directory:
```env
D_ID_API_KEY=your_d_id_api_key_here
```

### 3. Run Locally
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## ☁️ Deploy to Streamlit Community Cloud (GitHub)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - AI Talking Head Studio"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.name
   git push -u origin main
   ```

2. **Deploy on Streamlit Community Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io) and log in.
   - Click **New app** and select your GitHub repository.
   - Set **Main file path** to `app.py`.
   - Under **Advanced settings** -> **Secrets**, add your API key:
     ```toml
     D_ID_API_KEY = "your_d_id_api_key_here"
     ```
   - Click **Deploy**!

---

## ⚡ Quickstart: Next.js 14 App Router (Node.js)

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure API Key
Create `.env.local`:
```env
D_ID_API_KEY=your_d_id_api_key_here
```

### 3. Run Next.js Dev Server
```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🛠️ Project Structure

```
├── app.py                      # Streamlit primary web app entrypoint
├── requirements.txt            # Python dependencies for Streamlit Cloud
├── .streamlit/
│   └── config.toml             # Streamlit dark theme configuration
├── app/                        # Next.js 14 App Router
│   ├── api/talks/              # D-ID API server-side route proxy
│   ├── globals.css             # Tailwind CSS & ambient glows
│   └── page.tsx                # Next.js studio page
├── components/                 # React UI components (AvatarPicker, ScriptInput, etc.)
├── lib/                        # TypeScript types, constants & utils
├── .env.example                # Environment variables template
└── README.md
```

---

## 🔒 Security
`D_ID_API_KEY` is kept strictly server-side (in Next.js API route handlers or Streamlit backend execution). Never expose your secret key directly to client bundles.

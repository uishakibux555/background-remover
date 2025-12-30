# AI Background Remover (Local Web App)

A professional-grade, privacy-focused tool to remove image backgrounds using state-of-the-art AI models (**RMBG-2.0**, **BiRefNet**, **SAM 2.1**), running entirely on your local machine.

## ✨ Features
*   **Privacy First**: No images leave your computer. Everything runs locally.
*   **Best-in-Class Models**: Toggle between RMBG-2.0 (Best for Ecommerce), BiRefNet (General Purpose), and others.
*   **Split-View Slider**: Drag to see the "Before" (Solid Background) vs "After" (Transparency Checkerboard) effect.
*   **High Performance**: GPU acceleration supported (CUDA).

## 🚀 Quick Start (Windows)
We have included a "Magic Button" script to handle everything.

1.  **Double-click** `start_web_app.bat`.
2.  Wait for the console to say `Application startup complete`.
3.  The browser will open automatically to `http://localhost:5173`.
4.  **Enjoy!** Drag, drop, and slide.

---

## 🛠 Manual Installation (For Developers)

### 1. Backend (Python/FastAPI)
Required: Python 3.10+
```bash
# Navigate to project root
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

### 2. Frontend (React/Vite)
Required: Node.js 16+
```bash
cd frontend
npm install
npm run dev
```

## 📂 Project Structure
*   `backend/`: FastAPI server and AI model scripts (`rmbg2_remover.py`, etc).
*   `frontend/`: React + Vite user interface.
*   `processed/`: Output images are saved here.
*   `uploads/`: Temporary upload storage.

## 🤝 Contributing
Feel free to fork this project and submit Pull Requests!

## 📜 License
MIT License.

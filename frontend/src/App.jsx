import { useState, useRef } from 'react'
import axios from 'axios'
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [processedUrl, setProcessedUrl] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [model, setModel] = useState("rmbg2") // Default to SOTA/Newest

  // Handle Drag & Drop / File Select
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setProcessedUrl(null) // Reset result
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    const formData = new FormData()
    formData.append("file", selectedFile)
    formData.append("model_id", model)

    try {
      // Backend is on port 8000
      const response = await axios.post("http://localhost:8000/process", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })

      if (response.data.status === "success") {
        // Add random query param to force reload if name is same
        setProcessedUrl(response.data.processed_url + "?t=" + new Date().getTime())
      }
    } catch (error) {
      console.error("Error uploading:", error)
      alert("Failed to process image. Make sure Backend is running!")
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="bg-background-light dark:bg-background-dark text-gray-900 dark:text-gray-100 font-body min-h-screen flex flex-col transition-colors duration-200">

      {/* NAV */}
      <nav className="w-full px-6 py-4 flex justify-between items-center border-b-2 border-black dark:border-white bg-surface-light dark:bg-surface-dark sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <span className="material-icons-round text-primary text-4xl">layers</span>
          <span className="font-display text-3xl tracking-wide uppercase italic">BG REMOVER</span>
        </div>
        <div className="flex items-center gap-4">
          <button
            className="p-2 rounded-full border-2 border-black dark:border-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            onClick={() => document.documentElement.classList.toggle('dark')}
          >
            <span className="material-icons-round dark:hidden">dark_mode</span>
            <span className="material-icons-round hidden dark:block">light_mode</span>
          </button>
        </div>
      </nav>

      <main className="flex-grow flex flex-col items-center justify-center p-4 md:p-8 lg:p-12">
        <h1 className="font-display text-5xl md:text-7xl mb-8 text-center uppercase tracking-tighter">
          Remove Backgrounds <br className="md:hidden" /> <span className="text-primary italic">Instantly</span>
        </h1>

        <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* LEFT PANEL: UPLOAD & CONTROLS */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="mb-2">
              <p className="text-xl font-bold font-display uppercase tracking-wide">Welcome Back,</p>
              <p className="text-gray-600 dark:text-gray-400">Ready to transform your images?</p>
            </div>

            {/* Upload Card */}
            <div className="bg-[#1a1a1a] dark:bg-[#000000] p-6 rounded-3xl border-4 border-black dark:border-gray-700 slush-shadow slush-card transition-transform duration-200 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary opacity-10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>

              <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-gray-600 rounded-2xl bg-[#252525] dark:bg-[#111111] group-hover:border-primary transition-colors cursor-pointer relative">
                <input
                  type="file"
                  className="absolute inset-0 opacity-0 cursor-pointer z-10"
                  onChange={handleFileChange}
                  accept="image/*"
                />

                {previewUrl ? (
                  <img src={previewUrl} className="h-full w-full object-contain rounded-2xl p-2" />
                ) : (
                  <>
                    <div className="relative w-24 h-24 mb-4">
                      <div className="absolute inset-0 border-4 border-white rounded-2xl flex items-center justify-center overflow-hidden bg-gray-800">
                        <div className="absolute top-4 left-4 w-6 h-6 bg-primary rounded-full"></div>
                      </div>
                      <div className="absolute -bottom-2 -right-2 bg-primary text-black rounded-full p-1 border-2 border-[#1a1a1a]">
                        <span className="material-icons-round text-xl font-bold">arrow_upward</span>
                      </div>
                    </div>
                    <p className="text-gray-400 font-medium">Drag & Drop or Click</p>
                  </>
                )}
              </div>

              <button
                onClick={handleUpload}
                disabled={!selectedFile || isProcessing}
                className={`w-full mt-6 text-black font-display text-2xl uppercase tracking-wide py-4 rounded-xl border-2 border-black shadow-neobrutalism transition-all
                    ${!selectedFile ? 'bg-gray-500 cursor-not-allowed' : 'bg-primary hover:bg-orange-400 active:shadow-neobrutalism-sm active:translate-x-[2px] active:translate-y-[2px]'}
                `}
              >
                {isProcessing ? "Processing..." : "Upload Image"}
              </button>
            </div>

            {/* Model Selector Dropdown */}
            <div className="bg-surface-light dark:bg-surface-dark border-2 border-black dark:border-gray-500 rounded-2xl p-4 slush-shadow flex flex-col gap-2">
              <label className="font-display uppercase text-sm text-gray-500">Select Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-gray-100 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-xl px-4 py-3 font-bold focus:ring-primary focus:border-primary"
              >
                <option value="rmbg2">RMBG-2.0 (New & Best)</option>
                <option value="birefnet">BiRefNet (SOTA)</option>
                <option value="sam2">SAM 2.1 (Advanced)</option>
                <option value="u2net">U2Net (Standard)</option>
              </select>
            </div>

            <div className="bg-accent-blue/10 dark:bg-accent-blue/20 border-2 border-accent-blue rounded-2xl p-4 flex items-start gap-3">
              <span className="material-icons-round text-accent-blue">info</span>
              <p className="text-sm font-medium text-accent-blue dark:text-blue-300">
                <strong>Pro Tip:</strong> RMBG-2.0 is currently the best for e-commerce and difficult edges!
              </p>
            </div>
          </div>

          {/* RIGHT PANEL: RESULT SLIDER */}
          <div className="lg:col-span-8 flex flex-col h-full">
            <div className="bg-gray-200 dark:bg-gray-800 border-4 border-black dark:border-white rounded-3xl slush-shadow relative flex-grow min-h-[500px] overflow-hidden group flex items-center justify-center p-4">

              {!processedUrl && !isProcessing && (
                <div className="flex flex-col items-center justify-center text-center opacity-40">
                  <span className="material-icons-round text-6xl mb-4">image</span>
                  <p className="font-display text-2xl uppercase">Upload an image to start</p>
                </div>
              )}

              {isProcessing && (
                <div className="flex flex-col items-center justify-center text-center animate-pulse">
                  <span className="material-icons-round text-6xl mb-4 text-primary animate-spin">autorenew</span>
                  <p className="font-display text-2xl uppercase">Removing Background...</p>
                  <p className="text-sm text-gray-500">This might take a moment.</p>
                </div>
              )}

              {processedUrl && !isProcessing && (
                <div className="h-full w-full absolute inset-0 flex items-center justify-center p-4">
                  <ReactCompareSlider
                    itemOne={<ReactCompareSliderImage src={previewUrl} alt="Original" className="bg-white dark:bg-black" style={{ objectFit: "contain", maxHeight: "100%" }} />}
                    itemTwo={<ReactCompareSliderImage src={processedUrl} alt="Processed" className="bg-checkerboard" style={{ objectFit: "contain", maxHeight: "100%" }} />}
                    style={{ height: '100%', width: '100%' }}
                  />
                </div>
              )}


              {/* Labels */}
              <div className="absolute top-4 left-4 bg-black/50 text-white px-3 py-1 rounded-full text-xs font-bold backdrop-blur-sm pointer-events-none z-10">ORIGINAL</div>
              <div className="absolute top-4 right-4 bg-primary text-black px-3 py-1 rounded-full text-xs font-bold shadow-md pointer-events-none z-10">REMOVED</div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex flex-col sm:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-4 w-full justify-end">
                {processedUrl && (
                  <a
                    href={processedUrl}
                    download="removed_background.png"
                    className="bg-primary hover:bg-orange-400 text-black font-display text-2xl uppercase tracking-wide px-8 py-3 rounded-full border-2 border-black shadow-neobrutalism active:shadow-neobrutalism-sm active:translate-x-[2px] active:translate-y-[2px] transition-all flex items-center justify-center gap-2"
                  >
                    <span>Download</span>
                    <span className="material-icons-round">download</span>
                  </a>
                )}
              </div>
            </div>
          </div>

        </div>
      </main>

      <footer className="mt-12 py-8 px-6 border-t-2 border-black dark:border-gray-700 bg-surface-light dark:bg-surface-dark">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center gap-2 mb-4 md:mb-0">
            <span className="font-display text-xl uppercase italic">BG REMOVER</span>
            <span className="text-gray-500 text-sm">© 2025</span>
          </div>
          <div className="mt-4 md:mt-0 font-medium text-sm text-gray-600 dark:text-gray-400">
            Created by Shakib Shaikh
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

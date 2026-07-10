import { useState, useRef, useCallback, useEffect } from "react";
import {
  Upload,
  Film,
  Package,
  X,
  Play,
  ShoppingCart,
  Heart,
  Search,
  CheckCircle2,
  Loader2,
  Sparkles,
} from "lucide-react";

const API = "";

const styles = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Inter, system-ui, Arial, sans-serif; background: #0a0e17; color: #f0f4ff; }
  button { cursor: pointer; font: inherit; }
  input, textarea { font: inherit; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: rgba(255,255,255,0.04); }
  ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 99px; }

  .app { min-height: 100vh; display: flex; flex-direction: column; }

  .header {
    height: 72px; display: flex; align-items: center; justify-content: center;
    border-bottom: 1px solid rgba(255,255,255,0.06); flex-shrink: 0;
  }
  .header-inner {
    width: 100%; max-width: 1200px; padding: 0 28px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .brand { display: flex; align-items: center; gap: 12px; font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }
  .brand-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    display: flex; align-items: center; justify-content: center; font-size: 18px;
  }
  .brand span { background: linear-gradient(90deg, #e0e7ff, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

  .page { flex: 1; display: flex; align-items: center; justify-content: center; padding: 32px 28px; }
  .card {
    width: 100%; max-width: 860px; background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 24px;
    padding: 48px; backdrop-filter: blur(12px);
  }
  .card-title { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
  .card-subtitle { color: rgba(255,255,255,0.5); font-size: 15px; margin-bottom: 32px; }

  .drop-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
  .drop-zone {
    border: 2px dashed rgba(255,255,255,0.12); border-radius: 16px;
    padding: 40px 20px; text-align: center; transition: all 0.2s;
    position: relative; min-height: 200px;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
  }
  .drop-zone.dragging { border-color: #6366f1; background: rgba(99,102,241,0.06); }
  .drop-zone.has-file { border-color: rgba(255,255,255,0.08); padding: 16px; }
  .drop-icon { width: 40px; height: 40px; color: rgba(255,255,255,0.25); }
  .drop-label { font-size: 14px; color: rgba(255,255,255,0.45); }
  .drop-hint { font-size: 12px; color: rgba(255,255,255,0.25); }
  .drop-preview {
    width: 100%; height: 100%; object-fit: contain; border-radius: 12px;
    max-height: 180px;
  }
  .drop-remove {
    position: absolute; top: 8px; right: 8px; width: 28px; height: 28px;
    border-radius: 50%; border: none; background: rgba(0,0,0,0.6);
    color: white; display: flex; align-items: center; justify-content: center;
  }
  .drop-filename { font-size: 13px; color: rgba(255,255,255,0.6); margin-top: 6px; }

  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group label { font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 0.5px; }
  .form-group input, .form-group textarea {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 12px 14px; color: white; outline: none; transition: border-color 0.2s;
  }
  .form-group input:focus, .form-group textarea:focus { border-color: #6366f1; }
  .form-group textarea { resize: vertical; min-height: 80px; }

  .btn-primary {
    width: 100%; margin-top: 20px; padding: 16px;
    border: none; border-radius: 14px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    color: white; font-size: 16px; font-weight: 600;
    display: flex; align-items: center; justify-content: center; gap: 10px;
    transition: opacity 0.2s;
  }
  .btn-primary:hover { opacity: 0.9; }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

  .processing { text-align: center; padding: 40px 0; }
  .processing-icon { margin-bottom: 24px; }
  .processing h2 { font-size: 22px; font-weight: 600; margin-bottom: 8px; }
  .processing p { color: rgba(255,255,255,0.5); margin-bottom: 32px; }

  .progress-track {
    width: 100%; height: 6px; border-radius: 99px;
    background: rgba(255,255,255,0.06); overflow: hidden; margin-bottom: 24px;
  }
  .progress-fill {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    transition: width 0.5s ease;
  }
  .step-list { text-align: left; max-width: 400px; margin: 0 auto; }
  .step {
    display: flex; align-items: center; gap: 12px; padding: 10px 0;
    font-size: 14px; color: rgba(255,255,255,0.4);
  }
  .step.active { color: rgba(255,255,255,0.9); }
  .step.done { color: #34d399; }
  .step-icon { width: 20px; height: 20px; flex-shrink: 0; }

  .result-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
  .result-header h2 { font-size: 22px; font-weight: 600; }

  .video-wrap {
    width: 100%; border-radius: 16px; overflow: hidden;
    background: black; margin-bottom: 20px; position: relative;
  }
  .video-wrap video { width: 100%; display: block; max-height: 520px; }

  .product-card {
    display: grid; grid-template-columns: 100px 1fr; gap: 16px;
    padding: 16px; border-radius: 16px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 20px;
  }
  .product-thumb {
    width: 100px; height: 100px; border-radius: 12px; object-fit: cover;
    background: rgba(255,255,255,0.04);
  }
  .product-name { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
  .product-desc { font-size: 13px; color: rgba(255,255,255,0.5); margin-bottom: 8px; }
  .product-price { font-size: 20px; font-weight: 700; color: #a5b4fc; }

  .action-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px; }
  .action-btn {
    padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.03); color: white; font-size: 14px; font-weight: 500;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    transition: all 0.2s;
  }
  .action-btn:hover { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.14); }
  .action-btn.primary { background: linear-gradient(135deg, #6366f1, #a855f7); border: none; }
  .action-btn.primary:hover { opacity: 0.9; }
  .action-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .btn-secondary {
    width: 100%; padding: 14px; border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08); background: transparent;
    color: rgba(255,255,255,0.6); font-size: 14px; font-weight: 500;
    transition: all 0.2s;
  }
  .btn-secondary:hover { background: rgba(255,255,255,0.04); color: white; }

  .toast {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    padding: 14px 24px; border-radius: 14px;
    background: rgba(16, 24, 40, 0.96); border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px); font-size: 14px;
    display: flex; align-items: center; gap: 10px;
    z-index: 100; box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    animation: toast-in 0.3s ease;
  }
  @keyframes toast-in { from { opacity: 0; transform: translateX(-50%) translateY(12px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }

  .error-msg { color: #f87171; font-size: 13px; margin-top: 4px; }

  @media (max-width: 640px) {
    .drop-grid, .form-row, .action-grid { grid-template-columns: 1fr; }
    .card { padding: 28px 20px; }
  }
`;

function DropZone({ icon: Icon, label, hint, accept, file, onFile, mimePrefix }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f && f.type.startsWith(mimePrefix)) onFile(f);
  }, [onFile, mimePrefix]);

  const handleChange = (e) => {
    const f = e.target.files[0];
    if (f) onFile(f);
  };

  return (
    <div
      className={`drop-zone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !file && inputRef.current?.click()}
    >
      {file ? (
        <>
          {mimePrefix === "image/" ? (
            <img src={URL.createObjectURL(file)} alt="" className="drop-preview" />
          ) : (
            <video src={URL.createObjectURL(file)} className="drop-preview" />
          )}
          <div className="drop-filename">{file.name}</div>
          <button className="drop-remove" onClick={(e) => { e.stopPropagation(); onFile(null); }}>
            <X size={14} />
          </button>
        </>
      ) : (
        <>
          <Icon className="drop-icon" />
          <div className="drop-label">{label}</div>
          <div className="drop-hint">{hint}</div>
        </>
      )}
      <input ref={inputRef} type="file" accept={accept} onChange={handleChange} style={{ display: "none" }} />
    </div>
  );
}

function UploadPage({ onStartRender }) {
  const [video, setVideo] = useState(null);
  const [productImg, setProductImg] = useState(null);
  const [productName, setProductName] = useState("");
  const [productDesc, setProductDesc] = useState("");
  const [productPrice, setProductPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canRender = video && productImg && productName.trim();

  const handleRender = async () => {
    if (!canRender) return;
    setLoading(true); setError("");

    const form = new FormData();
    form.append("video", video);
    form.append("product_image", productImg);
    form.append("product_name", productName);
    form.append("product_description", productDesc || productName);
    if (productPrice) form.append("product_price", productPrice);

    try {
      const res = await fetch(`${API}/render`, { method: "POST", body: form });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `Server error: ${res.status}`);
      }
      const data = await res.json();
      onStartRender(data.job_id, {
        productName, productDesc: productDesc || productName, productPrice,
        productImage: URL.createObjectURL(productImg),
      });
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <div className="card-title">Add a product to your video</div>
        <div className="card-subtitle">Upload a video and a product image. We'll place it naturally into the scene.</div>

        <div className="drop-grid">
          <DropZone
            icon={Film} label="Upload your video"
            hint="MP4, MOV — any length" accept="video/*" mimePrefix="video/"
            file={video} onFile={setVideo}
          />
          <DropZone
            icon={Package} label="Upload product image"
            hint="PNG with transparency works best" accept="image/*" mimePrefix="image/"
            file={productImg} onFile={setProductImg}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Product name</label>
            <input
              placeholder="e.g. Wooden Coffee Table"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Price (optional)</label>
            <input
              placeholder="e.g. $249.99"
              value={productPrice}
              onChange={(e) => setProductPrice(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Description (optional)</label>
          <textarea
            placeholder="Describe the product for AI placement..."
            value={productDesc}
            onChange={(e) => setProductDesc(e.target.value)}
          />
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button className="btn-primary" disabled={!canRender || loading} onClick={handleRender}>
          {loading ? <Loader2 size={18} className="spin" /> : <Sparkles size={18} />}
          {loading ? "Uploading..." : "Render Product into Video"}
        </button>
      </div>
    </div>
  );
}

const STEPS = [
  "Analyzing scene structure",
  "Detecting placement surfaces",
  "Positioning product in scene",
  "Blending with AI generation",
  "Finalizing output video",
];

function ProcessingPage({ jobId }) {
  const [progress, setProgress] = useState(0);
  const [activeStep, setActiveStep] = useState(-1);

  useEffect(() => {
    let cancelled = false;
    const totalDuration = 25000;
    const stepInterval = totalDuration / STEPS.length;
    const start = Date.now();

    const tick = () => {
      if (cancelled) return;
      const elapsed = Date.now() - start;
      const pct = Math.min(elapsed / totalDuration, 1);
      setProgress(pct);
      setActiveStep(Math.min(Math.floor(elapsed / stepInterval), STEPS.length - 1));
      if (pct < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="page">
      <div className="card" style={{ maxWidth: 520 }}>
        <div className="processing">
          <div className="processing-icon">
            <Loader2 size={48} className="spin" style={{ color: "#6366f1", animation: "spin 1.5s linear infinite" }} />
          </div>
          <h2>Processing your video</h2>
          <p>Our AI is placing your product into the scene. This may take a minute.</p>

          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${progress * 100}%` }} />
          </div>

          <div className="step-list">
            {STEPS.map((s, i) => (
              <div key={s} className={`step ${i < activeStep ? "done" : i === activeStep ? "active" : ""}`}>
                {i < activeStep ? <CheckCircle2 className="step-icon" /> :
                 i === activeStep ? <Loader2 size={16} className="step-icon spin" style={{ animation: "spin 1s linear infinite" }} /> :
                 <div className="step-icon" />}
                {s}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultPage({ result, productInfo, onReset }) {
  const videoRef = useRef(null);
  const [toast, setToast] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 4000); };

  const callAgent = async (endpoint, body) => {
    setActionLoading(endpoint);
    try {
      const res = await fetch(`${API}${endpoint}`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
      });
      const data = await res.json();
      if (res.ok) showToast("Done! Check your browser.");
      else showToast(`Error: ${data.error || res.status}`);
    } catch (e) {
      showToast(`Error: ${e.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <div className="result-header">
          <CheckCircle2 size={24} style={{ color: "#34d399" }} />
          <h2>Your video is ready</h2>
        </div>

        <div className="video-wrap">
          {result?.video_url ? (
            <video ref={videoRef} src={result.video_url} controls autoPlay playsInline />
          ) : (
            <div style={{ padding: "80px 20px", textAlign: "center", color: "rgba(255,255,255,0.3)" }}>
              Rendered video will appear here
            </div>
          )}
        </div>

        <div className="product-card">
          <img src={productInfo.productImage} alt={productInfo.productName} className="product-thumb" />
          <div>
            <div className="product-name">{productInfo.productName}</div>
            <div className="product-desc">{productInfo.productDesc}</div>
            {productInfo.productPrice && <div className="product-price">{productInfo.productPrice}</div>}
          </div>
        </div>

        <div className="action-grid">
          <button
            className="action-btn"
            disabled={actionLoading === "/find-it-on-amazon"}
            onClick={() => callAgent("/find-it-on-amazon", {
              image_url: "frame_001.jpg",
              user_prompt: `Find ${productInfo.productName} on Amazon`,
            })}
          >
            {actionLoading === "/find-it-on-amazon" ? <Loader2 size={16} className="spin" /> : <Search size={16} />}
            Find on Amazon
          </button>
          <button
            className="action-btn primary"
            disabled={actionLoading === "/add-it-to-shopping-cart"}
            onClick={() => callAgent("/add-it-to-shopping-cart", {
              product_url: `https://www.amazon.ca/s?k=${encodeURIComponent(productInfo.productName)}`,
            })}
          >
            {actionLoading === "/add-it-to-shopping-cart" ? <Loader2 size={16} className="spin" /> : <ShoppingCart size={16} />}
            Add to Cart
          </button>
          <button
            className="action-btn"
            disabled={actionLoading === "/add-it-to-shopping-list"}
            onClick={() => callAgent("/add-it-to-shopping-list", {
              product_url: `https://www.amazon.ca/s?k=${encodeURIComponent(productInfo.productName)}`,
              list_name: "wishlist",
            })}
          >
            {actionLoading === "/add-it-to-shopping-list" ? <Loader2 size={16} className="spin" /> : <Heart size={16} />}
            Add to Wishlist
          </button>
        </div>

        <button className="btn-secondary" onClick={onReset}>
          <Upload size={16} /> Render Another
        </button>
      </div>

      {toast && <div className="toast"><CheckCircle2 size={18} style={{ color: "#34d399" }} />{toast}</div>}
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("upload");
  const [jobId, setJobId] = useState(null);
  const [productInfo, setProductInfo] = useState(null);
  const [result, setResult] = useState(null);

  const handleStartRender = (id, info) => {
    setJobId(id);
    setProductInfo(info);
    setPage("processing");
    setTimeout(() => {
      setResult({ job_id: id, video_url: null });
      setPage("result");
    }, 6000);
  };

  const handleReset = () => {
    setPage("upload");
    setJobId(null);
    setProductInfo(null);
    setResult(null);
  };

  return (
    <div className="app">
      <style>{styles}</style>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>

      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-icon">B</div>
            <span>BackstageCommercials</span>
          </div>
          <div style={{ fontSize: 13, color: "rgba(255,255,255,0.25)" }}>AI Product Placement</div>
        </div>
      </header>

      {page === "upload" && <UploadPage onStartRender={handleStartRender} />}
      {page === "processing" && <ProcessingPage jobId={jobId} />}
      {page === "result" && <ResultPage result={result} productInfo={productInfo} onReset={handleReset} />}
    </div>
  );
}

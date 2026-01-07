// --- Global Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== "undefined") lucide.createIcons();

  // Deteksi elemen video untuk menentukan apakah kita di halaman scanner
  const scannerVideo = document.getElementById("video");
  const guideline = document.getElementById("face-guideline");

  if (scannerVideo && guideline) {
    initScannerPage();
  }

  // Logika untuk halaman Tambah Wajah
  const addFaceForm = document.getElementById("addFaceForm");
  if (addFaceForm) initRegistrationPage();

  // Logika untuk halaman Riwayat
  const calendarEl = document.getElementById("calendar");
  if (calendarEl) initHistoryPage();
});

// ==========================================
// SCANNER PAGE LOGIC (FAST VERSION)
// ==========================================
function initScannerPage() {
  const video = document.getElementById("video");
  const guideline = document.getElementById("face-guideline");
  const statusText = document.getElementById("status-text");
  const canvas = document.getElementById("canvas");
  const loadingCircle = document.getElementById("loading-circle");
  const scanLabel = document.getElementById("scan-label");
  const container = document.getElementById("cam-container");

  let isProcessing = false;
  let scanProgress = 0;
  const MAX_OFFSET = 251.2;

  // --- Hanya Google Voice (Tanpa Bip) ---
  window.speak = function (text) {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const msg = new SpeechSynthesisUtterance(text);
      msg.lang = "id-ID";
      msg.rate = 1.0;
      window.speechSynthesis.speak(msg);
    }
  };

  window.updateStatus = function (txt, cls) {
    if (!statusText) return;
    statusText.innerText = txt;
    const dot = document.getElementById("status-dot");
    if (dot) dot.className = `w-2.5 h-2.5 rounded-full ${cls}`;
  };

  // --- Face Detection (MediaPipe) ---
  if (typeof FaceDetection !== "undefined") {
    const faceDetection = new FaceDetection({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`,
    });

    // Kecepatan deteksi (0.65 lebih sensitif/cepat)
    faceDetection.setOptions({ model: "short", minDetectionConfidence: 0.65 });

    faceDetection.onResults((results) => {
      if (results.detections.length > 0) {
        const det = results.detections[0].boundingBox;
        const rect = container.getBoundingClientRect();

        // Ukuran Ring (1.1 = Pas di wajah)
        const boxSize = Math.max(det.width * rect.width, det.height * rect.height) * 1.1;
        const centerX = (1 - det.xCenter) * rect.width; 
        const centerY = det.yCenter * rect.height;

        guideline.style.display = 'flex';
        guideline.style.width = boxSize + "px";
        guideline.style.height = boxSize + "px";
        guideline.style.left = (centerX - boxSize / 2) + "px";
        guideline.style.top = (centerY - boxSize / 2) + "px";

        if (scanProgress < 100) {
          // Progress Scan (4.0 = Sangat Cepat)
          scanProgress += 4.0; 
          const offset = MAX_OFFSET - (scanProgress / 100) * MAX_OFFSET;
          if (loadingCircle) loadingCircle.style.strokeDashoffset = offset;
          if (scanLabel) scanLabel.innerText = `SCANNING ${Math.floor(scanProgress)}%`;
        } else if (!isProcessing) {
          guideline.classList.add("locked-state");
          if (scanLabel) scanLabel.innerText = "VERIFYING...";
          processScan(video, canvas);
        }
      } else {
        resetUI();
      }
    });

    const camera = new Camera(video, {
      onFrame: async () => { await faceDetection.send({ image: video }); },
      width: 1280, height: 720,
    });
    camera.start();
  }

  function resetUI() {
    scanProgress = 0;
    guideline.style.display = 'none';
    guideline.classList.remove("locked-state");
    if (loadingCircle) loadingCircle.style.strokeDashoffset = MAX_OFFSET;
    if (scanLabel) scanLabel.innerText = "SEARCHING...";
  }

  async function processScan(videoEl, canvasEl) {
    if (isProcessing) return;
    isProcessing = true;
    updateStatus("Verifying...", "bg-blue-500");

    // Capture Cepat (Low Resolution untuk Speed)
    canvasEl.width = 320;
    canvasEl.height = 240;
    const ctx = canvasEl.getContext("2d");
    ctx.save();
    ctx.scale(-1, 1);
    ctx.drawImage(videoEl, -canvasEl.width, 0, canvasEl.width, canvasEl.height);
    ctx.restore();

    const base64 = canvasEl.toDataURL("image/jpeg", 0.5);

    try {
      const res = await fetch("/process_image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: base64 }),
      });
      const data = await res.json();

      if (data.status === "success") {
        updateStatus(data.nama.toUpperCase(), "bg-emerald-500");
        speak("Berhasil, " + data.nama);
        loadLogs();
        setTimeout(() => { isProcessing = false; resetUI(); }, 2000);
      } 
      else if (data.status === "already_present") {
        updateStatus("ALREADY DONE", "bg-yellow-500");
        speak("Anda sudah absen hari ini.");
        setTimeout(() => { isProcessing = false; resetUI(); }, 1500);
      } 
      else {
        updateStatus("UNKNOWN", "bg-red-500");
        speak("Wajah tidak dikenali.");
        setTimeout(() => { isProcessing = false; resetUI(); }, 1200);
      }
    } catch (e) {
      isProcessing = false;
      resetUI();
    }
  }

  async function loadLogs() {
    const logsContainer = document.getElementById("today-logs");
    if (!logsContainer) return;
    try {
      const r = await fetch("/api/today_log");
      const d = await r.json();
      logsContainer.innerHTML = d.map((l) => `
        <div class="p-3 bg-white/5 border border-white/5 rounded-xl flex items-center justify-between mb-2">
          <div>
            <p class="text-white font-bold text-xs uppercase">${l.nama}</p>
            <p class="text-[9px] text-slate-400 font-bold">${l.waktu}</p>
          </div>
        </div>
      `).join("");
    } catch (e) { console.error("Error loading logs", e); }
  }
  loadLogs();
}

// ==========================================
// REGISTRATION PAGE LOGIC
// ==========================================
function initRegistrationPage() {
  const video = document.getElementById("video");
  const areaCamera = document.getElementById("areaCamera");
  const areaUpload = document.getElementById("areaUpload");
  const tabCam = document.getElementById("tabCam");
  const tabUp = document.getElementById("tabUp");
  let activeMode = "camera";
  let stream = null;

  window.switchUI = function (mode) {
    if (activeMode === mode) return;
    activeMode = mode;
    if (tabCam) tabCam.classList.toggle("active", mode === "camera");
    if (tabUp) tabUp.classList.toggle("active", mode === "upload");
    if (mode === "camera") {
      areaCamera.removeAttribute("hidden");
      areaUpload.setAttribute("hidden", "");
      startCam();
    } else {
      areaUpload.removeAttribute("hidden");
      areaCamera.setAttribute("hidden", "");
      stopCam();
    }
  };

  window.startCam = async function () {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: "user" },
      });
      if (video) video.srcObject = stream;
    } catch (e) { console.error("Kamera error", e); }
  };

  window.stopCam = function () {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      stream = null;
    }
  };

  window.submitData = async function () {
    const nama = document.getElementById("nama").value.trim();
    if (!nama) return alert("Isi nama dulu!");
    
    const canvas = document.getElementById("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.scale(-1, 1);
    ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
    const imgBase64 = canvas.toDataURL("image/jpeg", 0.9);

    try {
      const r = await fetch("/register_face", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nama: nama, image: imgBase64 }),
      });
      const d = await r.json();
      if (d.status === "success") window.location.href = "/daftar_user";
      else alert("Gagal: " + d.message);
    } catch (e) { alert("Kesalahan koneksi."); }
  };

  startCam();
}

// ==========================================
// HISTORY PAGE LOGIC
// ==========================================
function initHistoryPage() {
  window.deleteLog = function (logId) {
    // 1. Konfirmasi kepada pengguna
    if (!confirm("Hapus data ini dari riwayat secara permanen?")) return;

    // 2. Kirim permintaan hapus ke server (Flask)
    fetch(`/delete_log/${logId}`, { 
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then((r) => r.json())
    .then((d) => {
        if (d.status === "success") {
            // --- INI PROSES REALTIME ---
            // Cari elemen baris tabel berdasarkan ID
            const row = document.getElementById(`log-${logId}`);
            
            if (row) {
                // Berikan efek transisi halus sebelum dihapus total
                row.style.opacity = "0";
                row.style.transform = "translateX(20px)";
                row.style.transition = "all 0.3s ease";

                // Setelah animasi selesai (300ms), hapus elemen dari DOM
                setTimeout(() => {
                    row.remove();
                    
                    // Update juga FullCalendar jika ada agar sinkron
                    if (window.calendarInstance) {
                        window.calendarInstance.refetchEvents();
                    }
                }, 300);
            }
        } else {
            alert("Gagal menghapus: " + d.message);
        }
    })
    .catch((e) => {
        console.error("Error:", e);
        alert("Terjadi kesalahan koneksi.");
    });
};

  window.deleteAllLogs = function () {
    if (confirm("PERINGATAN: Semua data akan dihapus permanen!")) {
      window.location.href = "/clear_logs";
    }
  };

  if (typeof FullCalendar !== "undefined") {
    const calendarEl = document.getElementById("calendar");
    const tooltip = document.getElementById("tooltip");

    window.calendarInstance = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      locale: "id",
      height: "100%",
      headerToolbar: { left: "prev,next", center: "title", right: "today" },
      events: "/api/calendar_events",
      eventContent: function (arg) {
        const p = arg.event.extendedProps;
        const cssClass = p.is_admin ? "pill-admin" : "pill-user";
        return {
          html: `<div class="custom-event-pill ${cssClass}">
                  <i data-lucide="${p.is_admin ? 'users' : 'check-circle'}" style="width:12px; height:12px;"></i>
                  <span>${p.is_admin ? p.count + ' User' : 'Hadir'}</span>
                </div>`,
        };
      },
      eventDidMount: () => { if (typeof lucide !== "undefined") lucide.createIcons(); },
      eventMouseEnter: function (info) {
        const p = info.event.extendedProps;
        const nameEl = document.getElementById("tooltip-name");
        const contentEl = document.getElementById("tooltip-time");
        if (nameEl) nameEl.innerText = p.is_admin ? "Rekap Harian" : p.nama;
        if (contentEl) {
          if (p.is_admin) {
            let html = (p.users || []).map(u => `
              <div class="flex justify-between items-center text-[10px] text-slate-300">
                <span>${u.nama}</span><span class="font-mono text-blue-400">${u.waktu}</span>
              </div>`).join("");
            contentEl.innerHTML = html || '<span class="text-slate-500 text-[10px]">Kosong</span>';
          } else {
            contentEl.innerHTML = `<div class="text-xs text-slate-400">Waktu Absen: <span class="text-white font-mono">${p.waktu}</span></div>`;
          }
        }
        if (tooltip) {
          tooltip.style.display = "block";
          const rect = info.el.getBoundingClientRect();
          tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 10}px`;
          tooltip.style.left = `${rect.left + window.scrollX + rect.width / 2 - tooltip.offsetWidth / 2}px`;
        }
      },
      eventMouseLeave: () => { if (tooltip) tooltip.style.display = "none"; },
    });
    window.calendarInstance.render();
  }
}
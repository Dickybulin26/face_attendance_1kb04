// --- Global Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }

  // --- Scanner Logic (Index Page) ---
  const scannerVideo = document.getElementById("video");
  const guideline = document.getElementById("face-guideline");

  // Check if we are on the scanner page (presence of guideline element is a good indicator)
  if (scannerVideo && guideline) {
    initScannerPage();
  }

  // --- Registration Logic (Tambah Wajah Page) ---
  const addFaceForm = document.getElementById("addFaceForm");
  if (addFaceForm) {
    initRegistrationPage();
  }

  // --- History Logic (Riwayat Page) ---
  const calendarEl = document.getElementById("calendar");
  if (calendarEl) {
    initHistoryPage();
  }
});

// ==========================================
// SCANNER PAGE LOGIC
// ==========================================
function initScannerPage() {
  const video = document.getElementById("video");
  const guideline = document.getElementById("face-guideline");
  const statusText = document.getElementById("status-text");
  const canvas = document.getElementById("canvas");
  let isProcessing = false;

  // --- Speech Synthesis ---
  window.speak = function (text) {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const msg = new SpeechSynthesisUtterance(text);
      msg.lang = "id-ID";
      msg.rate = 1.1;
      msg.pitch = 1.0;
      window.speechSynthesis.speak(msg);
    }
  };

  // --- Update Status UI ---
  window.updateStatus = function (txt, cls) {
    if (!statusText) return;
    statusText.innerText = txt;
    const dot = document.getElementById("status-dot");
    if (dot) dot.className = `w-2.5 h-2.5 rounded-full ${cls}`;
  };

  // --- Face Detection Setup ---
  if (typeof FaceDetection !== "undefined") {
    const faceDetection = new FaceDetection({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`,
    });

    faceDetection.setOptions({ model: "short", minDetectionConfidence: 0.75 });

    faceDetection.onResults((results) => {
      if (results.detections.length > 0) {
        const det = results.detections[0].boundingBox;
        const vW = video.offsetWidth;
        const vH = video.offsetHeight;

        guideline.classList.remove("hidden");
        guideline.style.width = det.width * vW + "px";
        guideline.style.height = det.height * vH + "px";
        guideline.style.left =
          vW - det.xCenter * vW - (det.width * vW) / 2 + "px";
        guideline.style.top = det.yCenter * vH - (det.height * vH) / 2 + "px";

        if (!isProcessing) processScan(video, canvas);
      } else {
        guideline.classList.add("hidden");
      }
    });

    const camera = new Camera(video, {
      onFrame: async () => {
        await faceDetection.send({ image: video });
      },
      width: 1280,
      height: 720,
    });
    camera.start();
  }

  // --- Process Scan API ---
  async function processScan(videoEl, canvasEl) {
    isProcessing = true;
    updateStatus("Verifying...", "bg-blue-500");

    canvasEl.width = 640;
    canvasEl.height = 480;
    const ctx = canvasEl.getContext("2d");
    ctx.save();
    ctx.scale(-1, 1);
    ctx.drawImage(videoEl, -canvasEl.width, 0, canvasEl.width, canvasEl.height);
    ctx.restore();

    const base64 = canvasEl.toDataURL("image/jpeg", 0.7);

    try {
      const res = await fetch("/process_image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: base64 }),
      });
      const data = await res.json();

      if (data.status === "success") {
        updateStatus(data.nama.toUpperCase(), "bg-emerald-500");
        speak("Absensi berhasil. Terima kasih " + data.nama);
        loadLogs();
        setTimeout(() => {
          isProcessing = false;
        }, 3000);
      } else if (data.status === "already_present") {
        updateStatus("DONE", "bg-green-500");
        speak("Anda sudah absen hari ini.");
        setTimeout(() => {
          isProcessing = false;
        }, 2000);
      } else {
        updateStatus("UNKNOWN", "bg-red-500");
        speak("Wajah tidak dikenali.");
        setTimeout(() => {
          isProcessing = false;
        }, 1200);
      }
    } catch (e) {
      isProcessing = false;
    }
  }

  // --- Load Logs ---
  async function loadLogs() {
    const logsContainer = document.getElementById("today-logs");
    if (!logsContainer) return;

    try {
      const r = await fetch("/api/today_log");
      const d = await r.json();
      logsContainer.innerHTML = d
        .map(
          (l) => `
                    <div class="p-3 bg-white/5 border border-white/5 rounded-xl flex items-center justify-between">
                        <div>
                            <p class="text-white font-bold text-xs uppercase">${l.nama}</p>
                            <p class="text-[9px] text-slate-400 font-bold">${l.waktu}</p>
                        </div>
                    </div>
                `
        )
        .join("");
    } catch (e) {
      console.error("Error loading logs", e);
    }
  }

  // Initial load
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

  // Make functions available globally for onclick handlers in HTML
  window.switchUI = function (mode) {
    if (activeMode === mode) return;
    activeMode = mode;

    // Update Button UI
    if (tabCam) {
      tabCam.classList.toggle("active", mode === "camera");
      tabCam.classList.toggle("text-slate-500", mode === "upload");
    }
    if (tabUp) {
      tabUp.classList.toggle("active", mode === "upload");
      tabUp.classList.toggle("text-slate-500", mode === "camera");
    }

    // Toggle Areas
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
      if (stream) stopCam();
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: "user" },
      });
      if (video) video.srcObject = stream;
    } catch (e) {
      console.error("Kamera error", e);
    }
  };

  window.stopCam = function () {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      stream = null;
    }
  };

  window.previewFile = function (input) {
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = (e) => {
        document.getElementById("imgPrev").src = e.target.result;
        document.getElementById("previewContainer").classList.remove("hidden");
        document.getElementById("placeholderUp").classList.add("hidden");
      };
      reader.readAsDataURL(input.files[0]);
    }
  };

  window.submitData = async function () {
    const nama = document.getElementById("nama").value.trim();
    if (!nama) return alert("Isi nama dulu!");

    let imgBase64 = "";
    const btn = document.getElementById("btnSubmit");
    const btnContent = document.getElementById("btnContent");

    if (activeMode === "camera") {
      const canvas = document.getElementById("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.scale(-1, 1);
      ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
      imgBase64 = canvas.toDataURL("image/jpeg", 0.9);
    } else {
      imgBase64 = document.getElementById("imgPrev").src;
    }

    if (!imgBase64 || imgBase64.includes("window.location"))
      return alert("Foto tidak ada!");

    // START LOADING
    btn.disabled = true;
    btnContent.innerHTML = `
            <div class="loader-container">
                <div class="loader-spinner"></div>
                <span class="tracking-[0.2em]">MEMPROSES...</span>
            </div>
        `;

    try {
      const r = await fetch("/register_face", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nama: nama, image: imgBase64 }),
      });
      const d = await r.json();

      if (d.status === "success") {
        window.location.href = "/daftar_user";
      } else {
        alert("Gagal: " + d.message);
        window.resetBtn();
      }
    } catch (e) {
      alert("Kesalahan koneksi.");
      window.resetBtn();
    }
  };

  window.resetBtn = function () {
    const btn = document.getElementById("btnSubmit");
    const btnContent = document.getElementById("btnContent");
    btn.disabled = false;
    btnContent.innerHTML = `
            Selesaikan Pendaftaran
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
        `;
    if (typeof lucide !== "undefined") lucide.createIcons();
  };

  // Initialize camera on load
  startCam();
}

// ==========================================
// HISTORY PAGE LOGIC
// ==========================================
function initHistoryPage() {
  // Expose functions to window for onclick handlers
  window.deleteLog = function (logId) {
    if (!confirm("Hapus data ini dari riwayat?")) return;
    fetch(`/delete_log/${logId}`, { method: "POST" })
      .then((r) => r.json())
      .then((d) => {
        if (d.status === "success") {
          const card = document.getElementById(`log-${logId}`);
          // Animasi hapus
          if (card) {
            card.style.transform = "translateX(20px)";
            card.style.opacity = "0";
            setTimeout(() => {
              card.remove();
              if (window.calendarInstance)
                window.calendarInstance.refetchEvents();
            }, 300);
          }
        }
      });
  };

  window.deleteAllLogs = function () {
    if (confirm("PERINGATAN: Semua data akan dihapus permanen!")) {
      window.location.href = "/clear_logs";
    }
  };

  // Initialize FullCalendar
  if (typeof FullCalendar !== "undefined") {
    const calendarEl = document.getElementById("calendar");
    const tooltip = document.getElementById("tooltip");

    window.calendarInstance = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      locale: "id",
      height: "100%", // Mengisi parent container
      headerToolbar: { left: "prev,next", center: "title", right: "today" }, // Layout Toolbar Modern
      events: "/api/calendar_events",

      // Render Event Custom (Pills)
      eventContent: function (arg) {
        const p = arg.event.extendedProps;
        const isAdm = p.is_admin;
        const cssClass = isAdm ? "pill-admin" : "pill-user";
        const iconName = isAdm ? "users" : "check-circle";
        const text = isAdm ? `${p.count} User` : "Hadir";

        return {
          html: `
                    <div class="custom-event-pill ${cssClass}">
                    <i data-lucide="${iconName}" style="width:12px; height:12px;"></i>
                    <span>${text}</span>
                    </div>
                `,
        };
      },

      eventDidMount: () => {
        if (typeof lucide !== "undefined") lucide.createIcons();
      },

      // Tooltip Logic
      eventMouseEnter: function (info) {
        const p = info.event.extendedProps;
        const nameEl = document.getElementById("tooltip-name");
        const contentEl = document.getElementById("tooltip-time");

        if (nameEl) nameEl.innerText = p.is_admin ? "Rekap Harian" : p.nama;

        if (contentEl) {
          if (p.is_admin) {
            let html = "";
            (p.users || []).forEach((u) => {
              html += `
                            <div class="flex justify-between items-center text-[10px] text-slate-300">
                                <span>${u.nama}</span>
                                <span class="font-mono text-blue-400">${u.waktu}</span>
                            </div>`;
            });
            contentEl.innerHTML =
              html || '<span class="text-slate-500 text-[10px]">Kosong</span>';
          } else {
            contentEl.innerHTML = `<div class="text-xs text-slate-400">Waktu Absen: <span class="text-white font-mono">${p.waktu}</span></div>`;
          }
        }

        // Positioning Tooltip
        if (tooltip) {
          tooltip.style.display = "block";
          const rect = info.el.getBoundingClientRect();
          // Center tooltip above event
          const top = rect.top + window.scrollY - tooltip.offsetHeight - 10;
          const left =
            rect.left +
            window.scrollX +
            rect.width / 2 -
            tooltip.offsetWidth / 2;

          tooltip.style.top = `${top}px`;
          tooltip.style.left = `${left}px`;
        }
      },

      eventMouseLeave: () => {
        if (tooltip) tooltip.style.display = "none";
      },
    });

    window.calendarInstance.render();
  }
}

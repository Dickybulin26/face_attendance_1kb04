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

  // --- User Database Logic (Daftar User Page) ---
  const userSearch = document.getElementById("userSearch");
  if (userSearch) {
    initUserDatabasePage();
  }

  // --- Mobile Menu Logic ---
  const mobileBtn = document.getElementById("mobile-menu-btn");
  const closeBtn = document.getElementById("close-menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");

  function toggleMenu() {
    mobileMenu.classList.toggle("hidden");
  }

  document.addEventListener("click", (e) => {
    if (mobileMenu && !mobileMenu.classList.contains("hidden")) {
      if (!mobileMenu.contains(e.target) && !mobileBtn.contains(e.target)) {
        mobileMenu.classList.add("hidden");
      }
    }
  });

  if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // Prevent immediate closing
      toggleMenu();
    });
  }

  if (closeBtn && mobileMenu) {
    closeBtn.addEventListener("click", toggleMenu);
  }

  // --- Login Logic (Login Page) ---
  const loginForm = document.querySelector("form.space-y-6");
  if (loginForm) {
    initLoginPage();
  }
});

// ==========================================
// LOGIN PAGE LOGIC
// ==========================================
function initLoginPage() {
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    const btn = this.querySelector("button");
    const originalText = btn.innerText;

    try {
      btn.disabled = true;
      btn.innerText = "Loading...";

      const response = await fetch("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (result.status === "success") {
        Swal.fire({
          icon: "success",
          title: "Login Berhasil!",
          text: "Mengalihkan ke dashboard...",
          showConfirmButton: false,
          timer: 1500,
          background: "#0f172a",
          color: "#fff",
        }).then(() => {
          window.location.href = result.redirect;
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Login Gagal",
          text: result.message || "Username/Password salah",
          background: "#0f172a",
          color: "#fff",
          confirmButtonColor: "#3b82f6",
        });
      }
    } catch (err) {
      Swal.fire({
        icon: "error",
        title: "System Error",
        text: "Gagal terhubung ke server",
        background: "#0f172a",
        color: "#fff",
      });
    } finally {
      btn.disabled = false;
      btn.innerText = originalText;
    }
  });
}

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

    const isMobile = window.innerWidth < 768;
    const camera = new Camera(video, {
      onFrame: async () => {
        await faceDetection.send({ image: video });
      },
      width: isMobile ? 720 : 1280,
      height: isMobile ? 1280 : 720,
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

      // Responsive Constraints
      const isMobile = window.innerWidth < 768;
      const constraints = {
        video: {
          facingMode: "user",
          width: isMobile ? { ideal: 720 } : { ideal: 1280 },
          height: isMobile ? { ideal: 1280 } : { ideal: 720 },
        },
      };

      stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (video) video.srcObject = stream;
    } catch (e) {
      console.error("Kamera error", e);
      Swal.fire({
        icon: "error",
        title: "Akses Kamera Gagal",
        text: "Pastikan izin kamera aktif dan tidak sedang digunakan aplikasi lain.",
        background: "#0f172a",
        color: "#fff",
        confirmButtonColor: "#3b82f6",
      });
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
    if (!nama) {
      return Swal.fire({
        icon: "warning",
        title: "Validasi Gagal",
        text: "Silahkan isi nama lengkap terlebih dahulu!",
        background: "#0f172a",
        color: "#fff",
        confirmButtonColor: "#3b82f6",
      });
    }

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

    if (!imgBase64 || imgBase64.includes("window.location")) {
      return Swal.fire({
        icon: "warning",
        title: "Foto Belum Ada",
        text: "Silahkan ambil foto atau upload gambar dulu!",
        background: "#0f172a",
        color: "#fff",
        confirmButtonColor: "#3b82f6",
      });
    }

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
        Swal.fire({
          icon: "success",
          title: "Berhasil!",
          text: "Data wajah berhasil didaftarkan.",
          showConfirmButton: false,
          timer: 1500,
          background: "#0f172a",
          color: "#fff",
        }).then(() => {
          window.location.href = "/daftar_user";
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Gagal",
          text: "Pastikan izin kamera aktif dan tidak sedang digunakan aplikasi lain.",
          background: "#0f172a",
          color: "#fff",
          confirmButtonColor: "#3b82f6",
        });
        window.resetBtn();
      }
    } catch (e) {
      Swal.fire({
        icon: "error",
        title: "System Error",
        text: "Gagal terhubung ke server.",
        background: "#0f172a",
        color: "#fff",
        confirmButtonColor: "#3b82f6",
      });
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

  // --- Search Logic ---
  const searchInput = document.getElementById("tableSearch");
  const tableRows = document.querySelectorAll(".log-row");
  const noLogsFound = document.getElementById("noLogsFound");

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const term = e.target.value.toLowerCase();
      let hasVisible = false;

      tableRows.forEach((row) => {
        const text = row.innerText.toLowerCase();
        const match = text.includes(term);
        row.style.display = match ? "" : "none";
        if (match) hasVisible = true;
      });

      if (noLogsFound) {
        if (hasVisible) {
          noLogsFound.classList.add("hidden");
        } else {
          noLogsFound.classList.remove("hidden");
        }
      }
    });
  }

  // Initialize FullCalendar
  if (typeof FullCalendar !== "undefined") {
    const calendarEl = document.getElementById("calendar");
    const tooltip = document.getElementById("calendar-tooltip");

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
        const text = isAdm ? `${p.count}` : "Hadir";

        return {
          html: `
                    <div class="custom-event-pill ${cssClass}">
                      <div class="flex justify-center items-center gap-2">
                        <i data-lucide="${iconName}" style="width:12px; height:12px;"></i>
                        <span>${text}</span>
                      </div>
                    </div>
                `,
        };
      },

      eventDidMount: (info) => {
        if (typeof lucide !== "undefined") lucide.createIcons();

        // Highlight Day Cell if it has events
        const dayCell = info.el.closest(".fc-daygrid-day");
        if (dayCell) {
          dayCell.classList.add("has-attendance");

          // Store data for hover
          const eventProps = info.event.extendedProps;

          // Attach Hover to the CELL (td), not just the event anchor
          dayCell.addEventListener("mouseenter", () =>
            showTooltip(eventProps, dayCell)
          );
          dayCell.addEventListener("mouseleave", () => hideTooltip());
        }
      },
    });

    window.calendarInstance.render();

    // Helper Functions for Tooltip
    function showTooltip(props, targetEl) {
      const tooltip = document.getElementById("calendar-tooltip");
      const nameEl = document.getElementById("tooltip-name");
      const contentEl = document.getElementById("tooltip-time");

      if (nameEl)
        nameEl.innerText = props.is_admin ? "Rekap Harian" : props.nama;

      if (contentEl) {
        if (props.is_admin) {
          let html = "";
          (props.users || []).forEach((u) => {
            html += `
                        <div class="flex justify-between items-center text-[10px] text-slate-300">
                            <span>${u.nama}</span>
                            <span class="font-mono text-blue-400">${u.waktu}</span>
                        </div>`;
          });
          contentEl.innerHTML =
            html || '<span class="text-slate-500 text-[10px]">Kosong</span>';
        } else {
          contentEl.innerHTML = `<div class="text-xs text-slate-400">Waktu Absen: <span class="text-white font-mono">${props.waktu}</span></div>`;
        }
      }

      if (tooltip) {
        tooltip.style.display = "block";
        const rect = targetEl.getBoundingClientRect();
        // Center tooltip above the CELL
        const top = rect.top + window.scrollY - tooltip.offsetHeight - 10;
        const left =
          rect.left + window.scrollX + rect.width / 2 - tooltip.offsetWidth / 2;

        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
      }
    }

    function hideTooltip() {
      const tooltip = document.getElementById("calendar-tooltip");
      if (tooltip) tooltip.style.display = "none";
    }
  }
}

// ==========================================
// USER DATABASE PAGE LOGIC
// ==========================================
function initUserDatabasePage() {
  const searchInput = document.getElementById("userSearch");
  const userRows = document.querySelectorAll(".user-row");
  const noResult = document.getElementById("noResult");

  if (searchInput) {
    searchInput.addEventListener("input", function (e) {
      const term = e.target.value.toLowerCase();
      let hasMatch = false;

      userRows.forEach((row) => {
        const data = row.getAttribute("data-search");
        if (data.includes(term)) {
          row.style.removeProperty("display");
          hasMatch = true;
        } else {
          row.style.display = "none";
        }
      });

      if (noResult) noResult.classList.toggle("hidden", hasMatch);
    });
  }

  window.toggleEdit = function (id) {
    const label = document.getElementById(`name-${id}`);
    const btn = document.getElementById(`btn-edit-${id}`);
    const iconEdit = document.getElementById(`icon-edit-${id}`);
    const iconSave = document.getElementById(`icon-save-${id}`);
    const isEditing = label.getAttribute("contenteditable") === "true";

    if (!isEditing) {
      label.setAttribute("contenteditable", "true");
      label.focus();
      btn.classList.add("border-blue-500", "bg-blue-500/10");
      iconEdit.classList.add("hidden");
      iconSave.classList.remove("hidden");

      // Move cursor to end
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(label);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
    } else {
      const newName = label.innerText.trim();
      if (newName) {
        saveEdit(id, newName);
      } else {
        alert("Nama tidak boleh kosong!");
      }
    }
  };

  window.saveEdit = function (id, newName) {
    fetch(`/edit_user/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nama: newName }),
    }).then((res) => {
      if (res.ok) {
        const label = document.getElementById(`name-${id}`);
        label.classList.add("text-emerald-400");
        setTimeout(() => location.reload(), 500);
      } else {
        alert("Database Sync Failed.");
      }
    });
  };

  window.deleteUser = function (id) {
    if (confirm("WARNING: Permanent deletion of biometric data. Proceed?")) {
      fetch(`/delete_user/${id}`, { method: "POST" }).then((res) => {
        if (res.ok) {
          const row = document.getElementById(`row-${id}`);
          row.style.transform = "translateX(50px)";
          row.style.opacity = "0";
          setTimeout(() => row.remove(), 300);
        }
      });
    }
  };
}

// app.js

// Use relative URL for API calls - works for both local dev and production
// When deployed, this will use the same domain as the frontend
const API_BASE = window.location.origin;

const newPatientForm = document.getElementById("new-patient-form");
const submitBtn = document.getElementById("submit-btn");
const formErrorEl = document.getElementById("form-error");

const queueBody = document.getElementById("queue-body");
const queueErrorEl = document.getElementById("queue-error");
const deptFilter = document.getElementById("department-filter");
const lastRefreshEl = document.getElementById("last-refresh");

const bedsBody = document.getElementById("beds-body");
const bedsErrorEl = document.getElementById("beds-error");

const patientsBody = document.getElementById("patients-body");
const patientsErrorEl = document.getElementById("patients-error");

const viewQueue = document.getElementById("view-queue");
const viewBeds = document.getElementById("view-beds");
const viewPatients = document.getElementById("view-patients");

const navQueue = document.getElementById("nav-queue");
const navBeds = document.getElementById("nav-beds");
const navPatients = document.getElementById("nav-patients");

let currentPatients = [];
let allPatients = []; // Store all patients for cross-reference in bed view

const modalBackdrop = document.getElementById("patient-modal-backdrop");
const modalCloseBtn = document.getElementById("patient-modal-close");

// ------------- API helper -------------

async function api(path, options = {}) {
  const url = API_BASE + path;
  const opts = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  };

  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return null;
  }
  return res.json();
}

// ------------- Formatting helpers -------------

function fmtMinutes(min) {
  if (min == null || Number.isNaN(min)) {
    return "–";
  }
  if (min < 1) return "<1 min";
  if (min === 1) return "1 min";
  return `${min} min`;
}

function getEsiClass(esi) {
  return `tag tag-esi-${esi}`;
}

// ------------- Queue rendering -------------

function renderQueue(patients) {
  currentPatients = patients;
  if (!Array.isArray(patients) || patients.length === 0) {
    queueBody.innerHTML = `<tr><td colspan="7" class="text-muted">No active patients in this department.</td></tr>`;
    return;
  }

  queueBody.innerHTML = "";

  patients.forEach((p) => {
    const tr = document.createElement("tr");

    const delayed = p.is_delayed;

    const nameCell = document.createElement("td");
    nameCell.innerHTML = `
      <div>
        <button class="link-button patient-name" data-patient-id="${p.id}">
          ${p.name}
        </button>
        <div class="text-xs text-muted">${p.chief_complaint || ""}</div>
        <div class="text-xs text-muted">ID: ${p.id.slice(0, 8)}…</div>
      </div>
    `;


    const esiCell = document.createElement("td");
    esiCell.innerHTML = `<span class="${getEsiClass(p.esi)}">ESI ${p.esi}</span>`;

    const statusCell = document.createElement("td");
    statusCell.innerHTML = `
      <div class="status-select-row">
        <select class="inline-select" data-patient-id="${p.id}">
          <option value="REGISTERED" ${p.status === "REGISTERED" ? "selected" : ""}>REGISTERED</option>
          <option value="AWAITING_TRIAGE" ${p.status === "AWAITING_TRIAGE" ? "selected" : ""}>AWAITING_TRIAGE</option>
          <option value="TRIAGED" ${p.status === "TRIAGED" ? "selected" : ""}>TRIAGED</option>
          <option value="AWAITING_BED" ${p.status === "AWAITING_BED" ? "selected" : ""}>AWAITING_BED</option>
          <option value="IN_BED" ${p.status === "IN_BED" ? "selected" : ""}>IN_BED</option>
          <option value="AWAITING_DISPOSITION" ${p.status === "AWAITING_DISPOSITION" ? "selected" : ""}>AWAITING_DISPOSITION</option>
          <option value="ADMITTED" ${p.status === "ADMITTED" ? "selected" : ""}>ADMITTED</option>
          <option value="DISCHARGED" ${p.status === "DISCHARGED" ? "selected" : ""}>DISCHARGED</option>
          <option value="LWBS" ${p.status === "LWBS" ? "selected" : ""}>LEFT W/O BEING SEEN</option>
        </select>
      </div>
    `;

    const waitCell = document.createElement("td");
    const waitText = fmtMinutes(p.time_in_current_status_minutes);
    const totalText = fmtMinutes(p.total_er_time_minutes);
    waitCell.innerHTML = `
      <div>
        <span class="pill ${delayed ? "tag-late" : ""}">${waitText}</span>
      </div>
      <div class="text-xs text-muted">Total: ${totalText}</div>
    `;

    const bedCell = document.createElement("td");
    bedCell.innerHTML = p.bed_id
      ? `<span class="pill">Bed ${p.bed_id.slice(0, 6)}…</span>`
      : `<span class="text-xs text-muted">Unassigned</span>`;

    const etaCell = document.createElement("td");
    etaCell.innerHTML = `
      <div class="row-actions">
        <button class="btn-small btn-secondary" data-eta-btn="${p.id}">Get ETA</button>
        <span class="eta-badge text-xs" id="eta-${p.id}" style="display:none;"></span>
      </div>
    `;

    const actionsCell = document.createElement("td");
    actionsCell.innerHTML = `
      <div class="row-actions">
        <button class="btn-small" data-save-status="${p.id}">Save status</button>
        <button class="btn-small" data-assign-bed="${p.id}">Assign bed</button>
      </div>
    `;

    tr.appendChild(nameCell);
    tr.appendChild(esiCell);
    tr.appendChild(statusCell);
    tr.appendChild(waitCell);
    tr.appendChild(bedCell);
    tr.appendChild(etaCell);
    tr.appendChild(actionsCell);

    queueBody.appendChild(tr);
  });
  
  wireRowButtons();
}

// ------------- Bed overview rendering -------------

function renderBeds(beds) {
  if (!Array.isArray(beds) || beds.length === 0) {
    bedsBody.innerHTML = `<tr><td colspan="6" class="text-muted">No beds found.</td></tr>`;
    return;
  }

  bedsBody.innerHTML = "";

  beds.forEach((b) => {
    const tr = document.createElement("tr");

    const nameCell = document.createElement("td");
    nameCell.textContent = b.section || b.id.slice(0, 8) + "…";

    const typeCell = document.createElement("td");
    typeCell.textContent = b.bed_type;

    const sectionCell = document.createElement("td");
    sectionCell.textContent = b.section;

    const featuresCell = document.createElement("td");
    featuresCell.textContent = (b.features || []).join(", ");

    const statusCell = document.createElement("td");
    statusCell.innerHTML = `<span class="pill">${b.status}</span>`;

    const patientCell = document.createElement("td");
    if (b.patient_id) {
      // Find patient in allPatients
      const patient = allPatients.find(p => p.id === b.patient_id);
      if (patient) {
        patientCell.innerHTML = `
          <button class="link-button patient-name" data-patient-id="${patient.id}">
            ${patient.name}
          </button>
        `;
      } else {
        patientCell.textContent = b.patient_id.slice(0, 8) + "…";
      }
    } else {
      patientCell.textContent = "—";
    }

    tr.appendChild(nameCell);
    tr.appendChild(typeCell);
    tr.appendChild(sectionCell);
    tr.appendChild(featuresCell);
    tr.appendChild(statusCell);
    tr.appendChild(patientCell);

    bedsBody.appendChild(tr);
  });

  // Wire up patient name click handlers for bed view
  wirePatientNameButtons();
}

function renderPatients(patients) {
  if (!Array.isArray(patients) || patients.length === 0) {
    patientsBody.innerHTML = `<tr><td colspan="8" class="text-muted">No patients found.</td></tr>`;
    return;
  }

  patientsBody.innerHTML = "";

  patients.forEach((p) => {
    const tr = document.createElement("tr");

    const nameCell = document.createElement("td");
    nameCell.innerHTML = `
      <div>
        <button class="link-button patient-name" data-patient-id="${p.id}">
          ${p.name}
        </button>
        <div class="text-xs text-muted">${p.chief_complaint || ""}</div>
      </div>
    `;

    const esiCell = document.createElement("td");
    esiCell.innerHTML = `<span class="${getEsiClass(p.esi)}">ESI ${p.esi}</span>`;

    const deptCell = document.createElement("td");
    deptCell.textContent = p.department || "ED";

    const statusCell = document.createElement("td");
    statusCell.innerHTML = `
      <div class="status-select-row">
        <select class="inline-select" data-patient-id="${p.id}">
          <option value="REGISTERED" ${p.status === "REGISTERED" ? "selected" : ""}>REGISTERED</option>
          <option value="AWAITING_TRIAGE" ${p.status === "AWAITING_TRIAGE" ? "selected" : ""}>AWAITING_TRIAGE</option>
          <option value="TRIAGED" ${p.status === "TRIAGED" ? "selected" : ""}>TRIAGED</option>
          <option value="AWAITING_BED" ${p.status === "AWAITING_BED" ? "selected" : ""}>AWAITING_BED</option>
          <option value="IN_BED" ${p.status === "IN_BED" ? "selected" : ""}>IN_BED</option>
          <option value="AWAITING_DISPOSITION" ${p.status === "AWAITING_DISPOSITION" ? "selected" : ""}>AWAITING_DISPOSITION</option>
          <option value="ADMITTED" ${p.status === "ADMITTED" ? "selected" : ""}>ADMITTED</option>
          <option value="DISCHARGED" ${p.status === "DISCHARGED" ? "selected" : ""}>DISCHARGED</option>
          <option value="LWBS" ${p.status === "LWBS" ? "selected" : ""}>LEFT W/O BEING SEEN</option>
        </select>
      </div>
    `;

    const bedCell = document.createElement("td");
    bedCell.textContent = p.bed_id ? p.bed_id.slice(0, 8) + "…" : "—";

    const arrivalCell = document.createElement("td");
    arrivalCell.textContent = p.arrival_ts
      ? new Date(p.arrival_ts).toLocaleTimeString()
      : "—";

    const totalCell = document.createElement("td");
    totalCell.textContent = fmtMinutes(p.total_er_time_minutes);

    const actionsCell = document.createElement("td");
    actionsCell.innerHTML = `
      <div class="row-actions">
        <button class="btn-small" data-save-status-db="${p.id}">Save</button>
      </div>
    `;

    tr.appendChild(nameCell);
    tr.appendChild(esiCell);
    tr.appendChild(deptCell);
    tr.appendChild(statusCell);
    tr.appendChild(bedCell);
    tr.appendChild(arrivalCell);
    tr.appendChild(totalCell);
    tr.appendChild(actionsCell);

    patientsBody.appendChild(tr);
  });

  wirePatientDbButtons();
  wirePatientNameButtons();
}

// ------------- Button wiring -------------
function wirePatientNameButtons() {
  // Open patient detail modal when clicking on name (works across all views)
  document.querySelectorAll(".patient-name").forEach((btn) => {
    btn.onclick = () => {
      const patientId = btn.getAttribute("data-patient-id");
      openPatientModal(patientId);
    };
  });
}

function wirePatientDbButtons() {
  // Save status in Patient Database view
  document.querySelectorAll("[data-save-status-db]").forEach((btn) => {
    btn.onclick = async () => {
      const patientId = btn.getAttribute("data-save-status-db");
      const select = document.querySelector(`select.inline-select[data-patient-id="${patientId}"]`);
      const status = select.value;
      const department = deptFilter.value;

      btn.disabled = true;
      try {
        await api(`/patients/${patientId}/status?department=${encodeURIComponent(department)}&status=${encodeURIComponent(status)}`, {
          method: "PATCH"
        });
        await loadPatientsDb();
      } catch (err) {
        alert("Failed to update status: " + err.message);
      } finally {
        btn.disabled = false;
      }
    };
  });
}

function findPatientById(patientId) {
  // First check currentPatients (queue view), then allPatients (database view)
  return currentPatients.find((p) => p.id === patientId) || allPatients.find((p) => p.id === patientId);
}

function openPatientModal(patientId) {
  const p = findPatientById(patientId);
  if (!p || !modalBackdrop) return;

  document.getElementById("modal-patient-name").textContent = p.name;
  document.getElementById("modal-patient-id").textContent = p.id;
  document.getElementById("modal-patient-esi").textContent = p.esi;
  document.getElementById("modal-patient-age").textContent = p.age ?? "—";
  document.getElementById("modal-patient-gender").textContent = p.gender ?? "—";
  document.getElementById("modal-patient-dept").textContent = p.department ?? deptFilter.value;
  document.getElementById("modal-patient-status").textContent = p.status;
  document.getElementById("modal-patient-bed").textContent = p.bed_id || "Unassigned";
  document.getElementById("modal-patient-wait").textContent = fmtMinutes(p.time_in_current_status_minutes);
  document.getElementById("modal-patient-total").textContent = fmtMinutes(p.total_er_time_minutes);
  document.getElementById("modal-patient-chief").textContent = p.chief_complaint || "—";
  document.getElementById("modal-patient-notes").textContent = p.notes || "—";

  modalBackdrop.style.display = "flex";
}

function closePatientModal() {
  if (!modalBackdrop) return;
  modalBackdrop.style.display = "none";
}

function wireRowButtons() {
  // Save status
  document.querySelectorAll("[data-save-status]").forEach((btn) => {
    btn.onclick = async () => {
      const patientId = btn.getAttribute("data-save-status");
      const select = document.querySelector(`select.inline-select[data-patient-id="${patientId}"]`);
      const status = select.value;
      const department = deptFilter.value;

      btn.disabled = true;
      try {
        await api(`/patients/${patientId}/status?department=${encodeURIComponent(department)}&status=${encodeURIComponent(status)}`, {
          method: "PATCH"
        });
        await loadQueue();
      } catch (err) {
        alert("Failed to update status: " + err.message);
      } finally {
        btn.disabled = false;
      }
    };
  });

  // Get ETA
  document.querySelectorAll("[data-eta-btn]").forEach((btn) => {
    btn.onclick = async () => {
      const patientId = btn.getAttribute("data-eta-btn");
      const department = deptFilter.value;
      const etaSpan = document.getElementById(`eta-${patientId}`);

      btn.disabled = true;
      etaSpan.style.display = "none";
      try {
        // Tweak rooms_available and avg_service_min for your demo
        const data = await api(
          `/eta/${patientId}?department=${encodeURIComponent(department)}&rooms_available=1&avg_service_min=20`
        );
        etaSpan.textContent = `${data.eta_minutes} min`;
        etaSpan.style.display = "inline-block";
      } catch (err) {
        alert("Failed to fetch ETA: " + err.message);
      } finally {
        btn.disabled = false;
      }
    };
  });

  // Wire patient name buttons
  wirePatientNameButtons();

  // Assign bed -> calls beds Database (DB) via /beds/assign_best
  document.querySelectorAll("[data-assign-bed]").forEach((btn) => {
    btn.onclick = async () => {
      const patientId = btn.getAttribute("data-assign-bed");
      const department = deptFilter.value; // use this as needed_bed_type
      btn.disabled = true;

      try {
        const body = {
          patient_id: patientId,
          needed_bed_type: department,
          needed_section: null,
          required_features: []
        };

        const assignedBed = await api(`/beds/assign_best`, {
          method: "POST",
          body: JSON.stringify(body)
        });

        alert(`Assigned bed ${assignedBed.id} (${assignedBed.section}) to patient ${patientId}`);
        await loadQueue();
        await loadBeds();
      } catch (err) {
        alert("Failed to assign bed: " + err.message);
      } finally {
        btn.disabled = false;
      }
    };
  });
}

// ------------- Loaders -------------

async function loadQueue() {
  const department = deptFilter.value;
  queueErrorEl.style.display = "none";

  try {
    const patients = await api(`/queue?department=${encodeURIComponent(department)}`);
    renderQueue(patients);
    const now = new Date();
    lastRefreshEl.textContent = `Last refresh: ${now.toLocaleTimeString()}`;
  } catch (err) {
    queueErrorEl.textContent = "Could not load queue: " + err.message;
    queueErrorEl.style.display = "block";
    queueBody.innerHTML = `<tr><td colspan="7" class="text-muted">Error loading queue</td></tr>`;
  }
}

async function loadBeds() {
  if (!bedsBody) return; // in case you remove bed overview
  bedsErrorEl.style.display = "none";
  try {
    // Load both beds and all patients so we can show patient names
    const [beds, patients] = await Promise.all([
      api(`/beds`),
      api(`/patients_db`)
    ]);
    allPatients = patients; // Store for cross-reference
    renderBeds(beds);
  } catch (err) {
    bedsErrorEl.textContent = "Could not load beds: " + err.message;
    bedsErrorEl.style.display = "block";
    bedsBody.innerHTML = `<tr><td colspan="6" class="text-muted">Error loading beds</td></tr>`;
  }
}

async function loadPatientsDb() {
  if (!patientsBody) return;
  patientsErrorEl.style.display = "none";
  try {
    const patients = await api(`/patients_db`);
    allPatients = patients; // Store for cross-reference in bed view
    renderPatients(patients);
  } catch (err) {
    patientsErrorEl.textContent = "Could not load patients: " + err.message;
    patientsErrorEl.style.display = "block";
    patientsBody.innerHTML = `<tr><td colspan="7" class="text-muted">Error loading patients</td></tr>`;
  }
}

// ------------- Event handlers -------------

// New patient form submit
newPatientForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  formErrorEl.style.display = "none";
  submitBtn.disabled = true;

  const formData = new FormData(newPatientForm);
  const payload = {
    name: formData.get("name"),
    esi: Number(formData.get("esi")),
    age: Number(formData.get("age")),
    gender: formData.get("gender"),
    chief_complaint: formData.get("chief_complaint"),
    department: formData.get("department"),
    notes: formData.get("notes") || null
  };

  try {
    await api(`/patients`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    newPatientForm.reset();
    newPatientForm.department.value = "ED";
    await loadQueue();
  } catch (err) {
    formErrorEl.textContent = "Failed to create patient: " + err.message;
    formErrorEl.style.display = "block";
  } finally {
    submitBtn.disabled = false;
  }
});

deptFilter.addEventListener("change", () => {
  loadQueue();
});

if (modalCloseBtn && modalBackdrop) {
  modalCloseBtn.addEventListener("click", closePatientModal);

  modalBackdrop.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) {
      closePatientModal();
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closePatientModal();
    }
  });
}

// ------------- Initial load & polling -------------
function showView(which) {
  if (viewQueue) viewQueue.style.display = which === "queue" ? "block" : "none";
  if (viewBeds) viewBeds.style.display = which === "beds" ? "block" : "none";
  if (viewPatients) viewPatients.style.display = which === "patients" ? "block" : "none";

  if (navQueue) navQueue.classList.toggle("nav-tab-active", which === "queue");
  if (navBeds) navBeds.classList.toggle("nav-tab-active", which === "beds");
  if (navPatients) navPatients.classList.toggle("nav-tab-active", which === "patients");

  if (which === "queue") {
    loadQueue();
  } else if (which === "beds") {
    loadBeds();
  } else if (which === "patients") {
    loadPatientsDb();
  }
}

if (navQueue) navQueue.addEventListener("click", () => showView("queue"));
if (navBeds) navBeds.addEventListener("click", () => showView("beds"));
if (navPatients) navPatients.addEventListener("click", () => showView("patients"));


// ------------- WebSocket Real-Time Updates -------------

// Connect to Socket.IO server - use current origin for both local and production
const socket = io(window.location.origin);

// Listen for connection
socket.on("connect", () => {
  console.log("WebSocket connected!");
});

// Listen for initial state snapshot
socket.on("state:snapshot", (data) => {
  console.log("Received state snapshot:", data);
  // Initial load happens below, so we can skip this or use it for faster initial render
});

// Listen for patient updates
socket.on("patient:created", async (patient) => {
  console.log("Patient created:", patient);
  await loadQueue();
  await loadPatientsDb();
});

socket.on("patient:updated", async (patient) => {
  console.log("Patient updated:", patient);
  await loadQueue();
  await loadPatientsDb();
});

// Listen for bed updates
socket.on("bed:updated", async (bed) => {
  console.log("Bed updated:", bed);
  await loadBeds();
  await loadQueue(); // Reload queue in case bed assignment affects display
});

socket.on("bed:created", async (bed) => {
  console.log("Bed created:", bed);
  await loadBeds();
});

socket.on("disconnect", () => {
  console.log("WebSocket disconnected");
});

socket.on("error", (error) => {
  console.error("WebSocket error:", error);
});

// ------------- Initial load -------------

showView("queue");     // start on Live Queue

// Optional: Keep polling as fallback (can remove if WebSocket is reliable)
// setInterval(loadQueue, 30_000);  // Reduced frequency since WebSocket handles updates
// setInterval(loadBeds, 60_000);


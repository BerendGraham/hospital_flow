// app.js

// Adjust this to match how you mount your router:
// e.g. "/v1" if you use app.include_router(router, prefix="/v1")
const API_BASE = "http://localhost:8000"; // add "/v1" if needed

const newPatientForm = document.getElementById("new-patient-form");
const submitBtn = document.getElementById("submit-btn");
const formErrorEl = document.getElementById("form-error");

const queueBody = document.getElementById("queue-body");
const queueErrorEl = document.getElementById("queue-error");
const deptFilter = document.getElementById("department-filter");
const lastRefreshEl = document.getElementById("last-refresh");

const bedsBody = document.getElementById("beds-body");
const bedsErrorEl = document.getElementById("beds-error");

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
        <div>${p.name}</div>
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
        <button class="btn-small btn-danger" data-discharge="${p.id}">Discharge</button>
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
    nameCell.textContent = b.id;

    const typeCell = document.createElement("td");
    typeCell.textContent = b.bed_type;

    const sectionCell = document.createElement("td");
    sectionCell.textContent = b.section;

    const featuresCell = document.createElement("td");
    featuresCell.textContent = (b.features || []).join(", ");

    const statusCell = document.createElement("td");
    statusCell.innerHTML = `<span class="pill">${b.status}</span>`;

    const patientCell = document.createElement("td");
    patientCell.textContent = b.patient_id ? b.patient_id.slice(0, 8) + "…" : "—";

    tr.appendChild(nameCell);
    tr.appendChild(typeCell);
    tr.appendChild(sectionCell);
    tr.appendChild(featuresCell);
    tr.appendChild(statusCell);
    tr.appendChild(patientCell);

    bedsBody.appendChild(tr);
  });
}

// ------------- Button wiring -------------

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
        await api(`/patients/${patientId}/status?department=${encodeURIComponent(department)}`, {
          method: "PATCH",
          body: JSON.stringify({ status })
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

  // Discharge
  document.querySelectorAll("[data-discharge]").forEach((btn) => {
    btn.onclick = async () => {
      const patientId = btn.getAttribute("data-discharge");
      const department = deptFilter.value;
      if (!confirm("Discharge this patient?")) return;

      btn.disabled = true;
      try {
        await api(`/discharge/${patientId}?department=${encodeURIComponent(department)}`, {
          method: "POST"
        });
        await loadQueue();
        await loadBeds();
      } catch (err) {
        alert("Failed to discharge patient: " + err.message);
      } finally {
        btn.disabled = false;
      }
    };
  });

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
    const beds = await api(`/beds`);
    renderBeds(beds);
  } catch (err) {
    bedsErrorEl.textContent = "Could not load beds: " + err.message;
    bedsErrorEl.style.display = "block";
    bedsBody.innerHTML = `<tr><td colspan="6" class="text-muted">Error loading beds</td></tr>`;
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

// ------------- Initial load & polling -------------

loadQueue();
loadBeds();
setInterval(loadQueue, 10_000);
setInterval(loadBeds, 30_000);

document.documentElement.dataset.js = "enabled";

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
const nativeFetch = window.fetch.bind(window);

function extractErrorMessage(payload, fallback) {
  if (typeof payload?.detail === "string" && payload.detail.trim()) return payload.detail;
  if (Array.isArray(payload?.detail)) {
    const details = payload.detail
      .map((item) => (typeof item?.msg === "string" ? item.msg : ""))
      .filter(Boolean);
    if (details.length) return details.join(" ");
  }
  if (typeof payload?.message === "string" && payload.message.trim()) return payload.message;
  return fallback;
}

window.fetch = (input, init = {}) => {
  const method = (init.method || "GET").toUpperCase();
  if (csrfToken && ["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const headers = new Headers(init.headers || {});
    headers.set("X-CSRF-Token", csrfToken);
    init.headers = headers;
  }
  return nativeFetch(input, init);
};

const workspaceMetrics = document.querySelector("#workspace-active-tasks");
if (workspaceMetrics) {
  nativeFetch("/dashboard")
    .then((response) => response.json())
    .then((payload) => {
      const pending = payload.deliveries?.pending || 0;
      const followUp = (payload.deliveries?.not_delivered || 0) + (payload.deliveries?.late || 0);
      workspaceMetrics.textContent = payload.active_tasks || 0;
      document.querySelector("#workspace-pending-deliveries").textContent = pending;
      document.querySelector("#workspace-follow-up").textContent = followUp;
      document.querySelector("#workspace-active-tasks-help").textContent = payload.active_tasks ? "En el año activo" : "Todavía no hay tareas creadas";
      document.querySelector("#workspace-pending-deliveries-help").textContent = pending ? "A la espera de una entrega" : "Su día está despejado";
      document.querySelector("#workspace-follow-up-help").textContent = followUp ? "Atrasadas o no entregadas" : "Las señales aparecerán aquí";
    })
    .catch(() => undefined);
}

const studentProfile = document.querySelector("#student-profile");
if (studentProfile) {
  nativeFetch(studentProfile.dataset.profileUrl)
    .then((response) => response.json().then((payload) => ({ response, payload })))
    .then(({ response, payload }) => {
       if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo cargar el perfil."));
      document.querySelector("#student-profile-name").textContent = payload.name;
      document.querySelector("#student-profile-meta").textContent = `NIE ${payload.nie}`;
      document.querySelector("#profile-task-count").textContent = payload.task_count;
      document.querySelector("#profile-completed").textContent = payload.counts.completed || 0;
      document.querySelector("#profile-compliance").textContent = `${payload.compliance_percentage}%`;
      document.querySelector("#student-profile-status").textContent = "Perfil conciliado con los registros de entregas.";
    })
    .catch((error) => {
      document.querySelector("#student-profile-name").textContent = "Perfil no disponible";
      document.querySelector("#student-profile-status").textContent = error.message;
    });
}

const yearSelect = document.querySelector("#follow-up-year");
const yearList = document.querySelector("#academic-years");
if (yearSelect || yearList) {
  nativeFetch("/academic-years")
    .then((response) => response.json())
    .then((years) => {
      years.forEach((year) => {
        if (yearSelect) {
          const option = document.createElement("option");
          option.value = year.id;
          option.textContent = `${year.label} (${year.status})`;
          yearSelect.append(option);
        }
        if (yearList) {
          const option = document.createElement("option");
          option.value = year.id;
          option.label = `${year.label} (${year.status})`;
          yearList.append(option);
        }
      });
     })
     .catch(() => undefined);
}

const loginForm = document.querySelector("#login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.querySelector("#login-message");
    const formData = new FormData(loginForm);
    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: formData.get("email"), password: formData.get("password") }),
      });
      if (!response.ok) throw new Error("El correo electrónico o la contraseña no son válidos.");
      window.location.assign("/workspace");
    } catch (error) {
      message.textContent = error.message;
    }
  });
}

const logoutButton = document.querySelector("#logout-button");
if (logoutButton) {
  logoutButton.addEventListener("click", async () => {
    const message = document.querySelector("#logout-message");
    logoutButton.disabled = true;
    message.textContent = "Cerrando sesión...";
    try {
      const response = await fetch("/auth/logout", { method: "POST" });
      if (!response.ok) throw new Error("No se pudo cerrar la sesión. Inténtelo de nuevo.");
      window.location.assign("/login");
    } catch (error) {
      message.textContent = error.message;
      logoutButton.disabled = false;
    }
  });
}

const taskYear = document.querySelector("#task-year");
if (taskYear) {
  nativeFetch("/organization/options")
    .then((response) => response.json())
    .then((options) => {
      [[taskYear, options.years], [document.querySelector("#task-subject"), options.subjects], [document.querySelector("#task-section"), options.sections]].forEach(([select, values]) => {
        values.forEach((item) => {
          const option = document.createElement("option");
          option.value = item.id;
          option.textContent = item.label;
          select.append(option);
        });
      });
    })
    .catch(() => undefined);
}

const taskSelectors = [document.querySelector("#roster-task-id"), document.querySelector("#edit-task-id")].filter(Boolean);
if (taskSelectors.length) {
  nativeFetch("/tasks/data")
    .then((response) => response.json())
    .then((tasks) => {
      taskSelectors.forEach((select) => {
        tasks.forEach((task) => {
          const option = document.createElement("option");
          option.value = task.id;
          option.textContent = `${task.title} (entrega: ${task.due_on})`;
          select.append(option);
        });
      });
    })
    .catch(() => undefined);
}

const importForm = document.querySelector("#import-form");
if (importForm) {
  const importYear = document.querySelector("#import-year");
  const importSection = document.querySelector("#import-section");
  const importFile = document.querySelector("#import-file");
  const importRows = document.querySelector("#import-rows");
  const importMessage = document.querySelector("#import-message");
  const importCommit = document.querySelector("#import-commit");
  let previewRows = [];
  nativeFetch("/organization/options").then((response) => response.json()).then((options) => {
    options.years.forEach((item) => { const option = document.createElement("option"); option.value = item.id; option.textContent = item.label; importYear.append(option); });
    options.sections.forEach((item) => { const option = document.createElement("option"); option.value = item.id; option.textContent = item.label; importSection.append(option); });
  }).catch(() => undefined);
  importForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!importFile.files[0]) return;
    const form = new FormData();
    form.append("file", importFile.files[0]);
    const response = await fetch("/students/imports/preview", { method: "POST", body: form });
    const payload = await response.json();
    if (!response.ok) { importMessage.textContent = extractErrorMessage(payload, "La vista previa falló."); return; }
    previewRows = payload.rows;
    importRows.replaceChildren(...previewRows.map((item) => {
      const row = document.createElement("tr");
      [item.row_number, item.nie, `${item.first_name} ${item.last_name}`, item.errors.join(", ") || "Válida"].forEach((value) => { const cell = document.createElement("td"); cell.textContent = value; row.append(cell); });
      return row;
    }));
    importCommit.disabled = payload.critical_errors > 0 || !importYear.value || !importSection.value;
    importMessage.textContent = payload.critical_errors ? `${payload.critical_errors} fila(s) requieren corrección.` : `${previewRows.length} fila(s) válidas listas para confirmar.`;
  });
  importCommit.addEventListener("click", async () => {
    const form = new FormData();
    form.append("file", importFile.files[0]);
    const query = new URLSearchParams({ academic_year_id: importYear.value, section_id: importSection.value });
    const response = await fetch(`/students/imports/commit?${query}`, { method: "POST", body: form });
    const payload = await response.json();
    importMessage.textContent = response.ok ? `${payload.imported} estudiante(s) importado(s).` : extractErrorMessage(payload, "La importación falló.");
     if (response.ok) {
       importCommit.disabled = true;
       await refreshStudentList();
     }
  });
}

async function submitJsonForm(form, endpoint, messageId, successMessage, redirect, includePassword = true) {
  const message = document.querySelector(messageId);
  const formData = new FormData(form);
  const body = { email: formData.get("email") };
  if (includePassword) body.password = formData.get("password");
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const payload = await response.json();
       if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo completar la solicitud."));
    message.textContent = successMessage(payload);
    if (redirect) window.setTimeout(() => window.location.assign(redirect), 600);
  } catch (error) {
    message.textContent = error.message;
  }
}

const registerForm = document.querySelector("#register-form");
if (registerForm) {
  registerForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitJsonForm(registerForm, "/auth/register", "#register-message", () => "Espacio de trabajo creado. Redirigiendo al inicio de sesión...", "/login");
  });
}

const recoveryForm = document.querySelector("#recovery-form");
if (recoveryForm) {
  recoveryForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitJsonForm(recoveryForm, "/auth/recovery", "#recovery-message", (payload) => payload.token ? `Token de recuperación: ${payload.token}` : "Si la cuenta existe, las instrucciones de recuperación están listas.", undefined, false);
  });
}

document.querySelectorAll("[data-json-form]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const message = document.getElementById(form.dataset.message);
    try {
      const response = await fetch(form.dataset.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const payload = await response.json();
       if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo completar la solicitud."));
      message.textContent = `Creado: ${payload.id || payload.name || payload.label}`;
    } catch (error) {
      message.textContent = error.message;
    }
  });
});

const subjectSectionForm = document.querySelector("#subject-section-form");
if (subjectSectionForm) {
  const subjectSelect = document.querySelector("#subject-section-subject");
  const sectionSelect = document.querySelector("#subject-section-section");
  const message = document.querySelector("#subject-section-message");
  nativeFetch("/organization/options")
    .then((response) => response.json().then((payload) => ({ response, payload })))
    .then(({ response, payload }) => {
      if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudieron cargar las asignaturas y secciones."));
      [[subjectSelect, payload.subjects], [sectionSelect, payload.sections]].forEach(([select, values]) => {
        values.forEach((item) => {
          const option = document.createElement("option");
          option.value = item.id;
          option.textContent = item.label;
          select.append(option);
        });
      });
    })
    .catch((error) => { message.textContent = error.message; });
  subjectSectionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(subjectSectionForm);
    const subjectId = data.get("subject_id");
    const sectionId = data.get("section_id");
    try {
      const response = await fetch(`/subjects/${encodeURIComponent(subjectId)}/sections/${encodeURIComponent(sectionId)}`, { method: "POST" });
      const payload = await response.json();
      if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo vincular la asignatura y la sección."));
      message.textContent = "La asignatura se vinculó a la sección.";
      subjectSectionForm.reset();
    } catch (error) {
      message.textContent = error.message;
    }
  });
}

const studentList = document.querySelector("#student-list-rows");
const studentListStatus = document.querySelector("#student-list-status");
const studentListFilters = document.querySelector("#student-list-filters");
const studentListYear = document.querySelector("#student-list-year");
const studentListSection = document.querySelector("#student-list-section");

async function refreshStudentList() {
  if (!studentList) return;
  studentListStatus.textContent = "Cargando estudiantes...";
  studentList.setAttribute("aria-busy", "true");
  const query = new URLSearchParams();
  if (studentListYear.value) query.set("academic_year_id", studentListYear.value);
  if (studentListSection.value) query.set("section_id", studentListSection.value);
  try {
    const response = await fetch(`/students${query.toString() ? `?${query}` : ""}`);
    const payload = await response.json();
     if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo cargar el listado de estudiantes."));
    if (!payload.length) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 5;
      cell.className = "muted";
      cell.textContent = "No hay estudiantes para los filtros seleccionados.";
      row.append(cell);
      studentList.replaceChildren(row);
    } else {
      studentList.replaceChildren(...payload.map((student) => {
        const row = document.createElement("tr");
        [student.nie, student.name, student.academic_year, student.section].forEach((value) => {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        });
        const profileCell = document.createElement("td");
        const link = document.createElement("a");
        link.href = `/students/${encodeURIComponent(student.id)}`;
        link.textContent = "Ver perfil";
        profileCell.append(link);
        row.append(profileCell);
        return row;
      }));
    }
    studentListStatus.textContent = `${payload.length} estudiante(s) encontrado(s).`;
  } catch (error) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent = error.message;
    row.append(cell);
    studentList.replaceChildren(row);
    studentListStatus.textContent = error.message;
  } finally {
    studentList.removeAttribute("aria-busy");
  }
}

if (studentList) {
  nativeFetch("/organization/options")
    .then((response) => response.json().then((payload) => ({ response, payload })))
    .then(({ response, payload }) => {
       if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudieron cargar los filtros."));
      payload.years.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = item.label;
        studentListYear.append(option);
      });
      payload.sections.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = item.label;
        studentListSection.append(option);
      });
    })
    .catch((error) => { studentListStatus.textContent = error.message; });
  studentListFilters.addEventListener("submit", (event) => {
    event.preventDefault();
    refreshStudentList();
  });
  refreshStudentList();
}

const studentForm = document.querySelector("#student-form");
if (studentForm) {
  studentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.querySelector("#student-message");
    try {
      const response = await fetch("/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(Object.fromEntries(new FormData(studentForm).entries())),
      });
      const payload = await response.json();
       if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo crear el estudiante."));
      message.textContent = `Se agregó ${payload.name} (${payload.nie}).`;
      studentForm.reset();
      await refreshStudentList();
    } catch (error) {
      message.textContent = error.message;
    }
  });
}

const rosterForm = document.querySelector("#roster-form");
if (rosterForm) {
  rosterForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const taskId = new FormData(rosterForm).get("task_id");
    const message = document.querySelector("#roster-message");
    const rows = document.querySelector("#roster-rows");
    try {
      const response = await fetch(`/tasks/${encodeURIComponent(taskId)}/roster`);
      const roster = await response.json();
       if (!response.ok) throw new Error(extractErrorMessage(roster, "No se pudo cargar la lista."));
       rows.replaceChildren(...roster.map((delivery) => rosterRow(delivery)));
       message.textContent = `Se cargaron ${roster.length} filas de entrega.`;
     } catch (error) {
       const row = document.createElement("tr");
       const cell = document.createElement("td");
       cell.colSpan = 5;
       cell.textContent = error.message;
       row.append(cell);
       rows.replaceChildren(row);
       message.textContent = error.message;
     }
  });
}

const taskEditForm = document.querySelector("#task-edit-form");
if (taskEditForm) {
  taskEditForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.querySelector("#task-edit-message");
    const data = new FormData(taskEditForm);
    const payload = {};
    const title = data.get("title");
    const dueOn = data.get("due_on");
    if (title) payload.title = title;
    if (dueOn) payload.due_on = dueOn;
    if (data.get("archived") === "on") payload.archived = true;
    try {
      const response = await fetch(`/tasks/${encodeURIComponent(data.get("task_id"))}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
       if (!response.ok) throw new Error(extractErrorMessage(result, "No se pudo actualizar la tarea."));
      message.textContent = `Se guardó ${result.title}.`;
    } catch (error) {
      message.textContent = error.message;
    }
  });
}

function rosterRow(delivery) {
  const row = document.createElement("tr");
  const studentName = delivery.student_name || "Estudiante sin nombre";
  const studentNie = delivery.student_nie || "NIE no disponible";
  const statusLabels = {
    pending: "Pendiente",
    delivered: "Entregada",
    not_delivered: "No entregada",
    late: "Atrasada",
    completed: "Completada",
  };
  const identityCell = document.createElement("td");
  const identity = document.createElement("div");
  identity.className = "student-identity";
  const name = document.createElement("strong");
  name.textContent = studentName;
  const nie = document.createElement("small");
  nie.textContent = `NIE ${studentNie}`;
  identity.append(name, nie);
  identityCell.append(identity);

  const statusCell = document.createElement("td");
  statusCell.className = "status-cell";
  const status = document.createElement("span");
  status.className = "status-label";
  const deliveryDate = document.createElement("span");
  deliveryDate.className = "delivery-date";
  const select = document.createElement("select");
  select.setAttribute("aria-label", `Estado de entrega para ${studentName}`);
  Object.entries(statusLabels).forEach(([value, label]) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    select.append(option);
  });
  statusCell.append(status, select, deliveryDate);

  const evidenceCell = document.createElement("td");
  const evidence = document.createElement("div");
  evidence.className = "evidence-control";
  const evidenceSummary = document.createElement("small");
  evidenceSummary.append("Evidencias: ");
  const evidenceCount = document.createElement("span");
  evidenceCount.className = "evidence-count";
  evidenceCount.textContent = delivery.evidence_count;
  evidenceSummary.append(evidenceCount);
  const fileId = `evidence-${delivery.id}`;
  const fileLabel = document.createElement("label");
  fileLabel.className = "file-picker";
  fileLabel.htmlFor = fileId;
  const fileLabelText = document.createElement("span");
  fileLabelText.textContent = "Elegir archivo";
  const fileName = document.createElement("span");
  fileName.className = "file-name";
  fileName.textContent = "Ningún archivo";
  fileLabel.append(fileLabelText, fileName);
  const file = document.createElement("input");
  file.id = fileId;
  file.className = "file-input";
  file.type = "file";
  file.accept = ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.webp";
  file.setAttribute("aria-label", `Evidencia para ${studentName}`);
  file.addEventListener("change", () => {
    fileName.textContent = file.files[0]?.name || "Ningún archivo";
  });
  evidence.append(evidenceSummary, fileLabel, file);
  evidenceCell.append(evidence);

  const noteCell = document.createElement("td");
  noteCell.className = "note-cell";
  const observationSummary = document.createElement("small");
  observationSummary.append("Notas: ");
  const observationCount = document.createElement("span");
  observationCount.className = "observation-count";
  observationCount.textContent = delivery.observation_count;
  observationSummary.append(observationCount);
  const observationInput = document.createElement("textarea");
  observationInput.className = "observation-input";
  observationInput.rows = 2;
  observationInput.placeholder = "Observación privada";
  observationInput.setAttribute("aria-label", `Observación privada para ${studentName}`);
  const addObservation = document.createElement("button");
  addObservation.className = "button button-secondary add-observation";
  addObservation.type = "button";
  addObservation.textContent = "Agregar nota";
  noteCell.append(observationSummary, observationInput, addObservation);

  const actionCell = document.createElement("td");
  const actions = document.createElement("div");
  actions.className = "roster-action";
  const button = document.createElement("button");
  button.className = "button button-secondary save-delivery";
  button.type = "button";
  button.textContent = "Guardar estado";
  const historyButton = document.createElement("button");
  historyButton.className = "button button-secondary history-delivery";
  historyButton.type = "button";
  historyButton.textContent = "Ver historial";
  const rowMessage = document.createElement("span");
  rowMessage.className = "row-message";
  rowMessage.setAttribute("role", "status");
  actions.append(button, historyButton, rowMessage);
  actionCell.append(actions);
  row.append(identityCell, statusCell, evidenceCell, noteCell, actionCell);
  select.value = delivery.status;
  status.textContent = statusLabels[delivery.status] || "Estado no disponible";
  deliveryDate.textContent = formatDeliveryDate(delivery.actual_delivered_at);
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      const selectedStatus = select.value;
      const payloadBody = { status: selectedStatus };
      if (["delivered", "completed"].includes(selectedStatus)) {
        payloadBody.actual_delivered_at = new Date().toISOString();
      } else {
        payloadBody.actual_delivered_at = null;
      }
      const response = await fetch(`/deliveries/${delivery.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payloadBody) });
      const payload = await response.json();
     if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo guardar el estado de la entrega."));
       status.textContent = statusLabels[payload.status] || "Estado no disponible";
       deliveryDate.textContent = formatDeliveryDate(payload.actual_delivered_at);
       if (file.files[0]) {
        const form = new FormData();
        form.append("file", file.files[0]);
        const upload = await fetch(`/deliveries/${delivery.id}/evidence`, { method: "POST", body: form });
        if (!upload.ok) throw new Error("Se guardó el estado, pero falló la carga de evidencia.");
        evidenceCount.textContent = Number(evidenceCount.textContent) + 1;
        file.value = "";
        fileName.textContent = "Ningún archivo";
      }
      rowMessage.textContent = "Entrega guardada.";
    } catch (error) {
      window.alert(error.message);
    } finally {
      button.disabled = false;
    }
  });
  addObservation.addEventListener("click", async () => {
     const body = observationInput.value.trim();
    if (!body) return;
    try {
      const response = await fetch(`/deliveries/${delivery.id}/observations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ body }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo agregar la nota."));
       observationCount.textContent = Number(observationCount.textContent) + 1;
      rowMessage.textContent = "Nota privada agregada.";
       observationInput.value = "";
    } catch (error) {
      rowMessage.textContent = error.message;
    }
  });
  historyButton.addEventListener("click", async (event) => {
    const historyButton = event.currentTarget;
    historyButton.disabled = true;
    try {
      const response = await fetch(`/deliveries/${delivery.id}/history`);
      const payload = await response.json();
      if (!response.ok) throw new Error(extractErrorMessage(payload, "No se pudo cargar el historial."));
      rowMessage.textContent = `${payload.events.length} eventos del historial.`;
    } catch (error) {
      rowMessage.textContent = error.message;
    } finally {
      historyButton.disabled = false;
    }
  });
  return row;
}

function formatDeliveryDate(value) {
  if (!value) return "Sin registrar";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Fecha no disponible";
  return date.toLocaleString("es-ES");
}

const studentSearch = document.querySelector("#student-search");
const followUpYear = document.querySelector("#follow-up-year");
if (followUpYear) {
  const refreshMetrics = async () => {
    const query = followUpYear.value.trim() ? `?academic_year_id=${encodeURIComponent(followUpYear.value.trim())}` : "";
    const response = await fetch(`/dashboard${query}`);
    if (!response.ok) return;
    const payload = await response.json();
    Object.entries(payload.deliveries).forEach(([status, count]) => {
      const target = document.querySelector(`[data-metric="${status}"]`);
      if (target) target.textContent = count;
    });
  };
  followUpYear.addEventListener("change", refreshMetrics);
  refreshMetrics();
}
if (studentSearch) {
  let searchTimer;
  studentSearch.addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(async () => {
      const results = document.querySelector("#student-results");
      try {
        const response = await fetch(`/search?q=${encodeURIComponent(studentSearch.value)}`);
        const payload = await response.json();
        if (!response.ok) throw new Error(extractErrorMessage(payload, "La búsqueda falló."));
        results.replaceChildren(...(payload.students.length ? payload.students.map((student) => {
          const item = document.createElement("li");
          const details = document.createElement("span");
          const name = document.createElement("strong");
          const nie = document.createElement("small");
          name.textContent = student.name;
          nie.textContent = student.nie;
          details.append(name, document.createElement("br"), nie);
          const link = document.createElement("a");
          link.href = `/students/${encodeURIComponent(student.id)}`;
          link.textContent = "Ver perfil";
          item.append(details, link);
          return item;
        }) : [Object.assign(document.createElement("li"), { textContent: "No hay estudiantes coincidentes." })]));
      } catch (error) {
        const item = document.createElement("li");
        item.textContent = error.message;
        results.replaceChildren(item);
      }
    }, 250);
  });
}

const reportForm = document.querySelector("#report-form");
if (reportForm) {
  reportForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = document.querySelector("#report-message");
    const id = document.querySelector("#report-student-id").value;
    const format = document.querySelector("#report-format").value;
    const year = document.querySelector("#report-year-id").value.trim();
    const query = new URLSearchParams({ format });
    if (year) query.set("academic_year_id", year);
    const reportWindow = window.open(`/reports/individual/${encodeURIComponent(id)}?${query}`, "_blank", "noopener");
    message.textContent = reportWindow ? "El informe se abrió en una pestaña nueva." : "Permita las ventanas emergentes para abrir el informe.";
  });
  const yearInput = document.querySelector("#report-year-id");
  const scopedLinks = document.querySelectorAll(".scoped-report");
  yearInput.addEventListener("input", () => {
    scopedLinks.forEach((link) => {
      const [path, rawQuery] = link.dataset.reportBase.split("?");
      const query = new URLSearchParams(rawQuery);
      if (yearInput.value.trim()) query.set("academic_year_id", yearInput.value.trim());
      else query.delete("academic_year_id");
      link.href = `${path}?${query}`;
    });
  });
}

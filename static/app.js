document.addEventListener("DOMContentLoaded", () => {
  // ---- Cache DOM elements ----
  const fileInput = document.getElementById("csv-file-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const loadSampleBtn = document.getElementById("load-sample-btn");
  const uploadForm = document.getElementById("upload-form");
  const generateReportBtn = document.getElementById("generate-report-btn");
  const generatePdfBtn = document.getElementById("generate-pdf-btn");
  
  // UI Interactive Elements
  const toggleBaselineBtn = document.getElementById("toggle-baseline-btn");
  const baselineDetailsPanel = document.getElementById("baseline-details-panel");
  const contactCustomerBtn = document.getElementById("contact-customer-btn");
  const contactDrawer = document.getElementById("contact-drawer");
  const closeDrawerBtn = document.getElementById("close-drawer-btn");
  const auditedReportsQueue = document.getElementById("audited-reports-queue");

  let latestNarrative = null;

  const resultBlocks = {
    riskStatus: document.getElementById("risk-status"),
    riskIndicators: document.getElementById("risk-indicators"),
    transactionsOfInterest: document.getElementById("transactions-of-interest"),
    customerBaseline: document.getElementById("customer-baseline"),
    investigationSummary: document.getElementById("investigation-summary"),
    investigatorPriority: document.getElementById("investigator-priority"),
  };

  let dataSource = null;

  // ---- File status container ----
  const fileStatusContainer = document.createElement("div");
  fileStatusContainer.style.cssText = "display: flex; align-items: center; gap: 10px; margin-top: 6px;";

  const fileStatus = document.createElement("p");
  fileStatus.id = "file-status";
  fileStatus.className = "placeholder-text";
  fileStatus.style.margin = "0";

  const clearFileBtn = document.createElement("button");
  clearFileBtn.type = "button";
  clearFileBtn.textContent = "Remove";
  clearFileBtn.style.cssText = "display: none; padding: 2px 8px; font-size: 0.75rem; background: #374151; color: #f3f4f6; border: 1px solid #4b5563; border-radius: 4px; cursor: pointer;";

  fileStatusContainer.appendChild(fileStatus);
  fileStatusContainer.appendChild(clearFileBtn);
  fileInput.insertAdjacentElement("afterend", fileStatusContainer);

  function setFileStatus(message, isFileLoaded = false) {
    fileStatus.textContent = message;
    if (isFileLoaded) {
      fileInput.disabled = true; // Lock file input when CSV is loaded
      clearFileBtn.style.display = "inline-block";
    } else {
      fileInput.disabled = false;
      clearFileBtn.style.display = "none";
    }
  }

  clearFileBtn.addEventListener("click", () => {
    fileInput.value = "";
    dataSource = null;
    setFileStatus("No file selected.", false);
    resetAllResults();
  });

  // Helper: Format arrays or text blocks as HTML bulleted lists WITHOUT removing Card Titles
  function renderAsList(container, items) {
    if (!container) return;
    
    // Preserve existing card title (h3, h4, or .card-tile-title) if present inside container
    const existingTitle = container.querySelector("h3, h4, .card-tile-title, .widget-title");
    const titleHtml = existingTitle ? existingTitle.outerHTML : "";

    if (!items || items.length === 0) {
      container.innerHTML = `${titleHtml}<p class="placeholder-text">None detected.</p>`;
      return;
    }
    const listHtml = `<ul class="formatted-bullet-list">${items.map(item => `<li>${item}</li>`).join("")}</ul>`;
    container.innerHTML = `${titleHtml}${listHtml}`;
  }

  // ---- Reset result blocks preserving titles ----
  function resetResultBlock(block, message) {
    if (!block) return;
    const existingTitle = block.querySelector("h3, h4, .card-tile-title, .widget-title");
    const titleHtml = existingTitle ? existingTitle.outerHTML : "";
    block.innerHTML = `${titleHtml}<p class="placeholder-text">${message}</p>`;
  }

  function resetAllResults() {
    resetResultBlock(resultBlocks.riskStatus, "Analysis has not been run yet.");
    resetResultBlock(resultBlocks.riskIndicators, "Risk indicators will appear here after analysis.");
    resetResultBlock(resultBlocks.transactionsOfInterest, "Flagged transactions will appear here after analysis.");
    resetResultBlock(resultBlocks.investigatorPriority, "Suggested priority level will appear here after analysis.");
    resetResultBlock(resultBlocks.customerBaseline, "Baseline behavior summary will appear here after analysis.");
    resetResultBlock(resultBlocks.investigationSummary, 'Click "Generate AI Narrative Analysis" to generate the investigation summary and recommendations.');
  }

  // ---- Helper: Add entry to Audited Session Log with CUSTOMER NAME ----
  function appendAuditLogEntry(fileName, classification, signalCount, customerName = null) {
    if (!auditedReportsQueue) return;

    const placeholder = auditedReportsQueue.querySelector(".placeholder-text");
    if (placeholder) {
      placeholder.remove();
    }

    const classificationLower = (classification || "").toLowerCase();
    
    let badgeColor = "#10b981"; // Green default
    let badgeBg = "rgba(16, 185, 129, 0.15)";
    let riskLabel = "LOW RISK";
    let targetGroupId = "queue-group-low";

    if (signalCount >= 4 || classificationLower.includes("high") || classificationLower.includes("critical") || classificationLower.includes("suspicious")) {
      badgeColor = "#e11d48"; // Red (High risk)
      badgeBg = "rgba(225, 29, 72, 0.15)";
      riskLabel = "HIGH RISK";
      targetGroupId = "queue-group-high";
    } else if (signalCount >1 || classificationLower.includes("medium") || classificationLower.includes("elevated") || classificationLower.includes("warning")) {
      badgeColor = "#d97706"; // Gold/Amber (Elevated)
      badgeBg = "rgba(217, 119, 6, 0.15)";
      riskLabel = "ELEVATED";
      targetGroupId = "queue-group-elevated";
    }

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const displayName = customerName ? customerName : fileName;

    const logItem = document.createElement("div");
    logItem.className = "report-item";
    logItem.style.borderLeftColor = badgeColor;

    logItem.innerHTML = `
      <div class="report-item-info">
        <span class="report-customer-name">${displayName}</span>
        <span class="report-meta-sub">${timestamp} — ${signalCount} signal(s) flagged (${fileName})</span>
      </div>
      <span class="status-badge" style="color: ${badgeColor}; background: ${badgeBg};">${riskLabel}</span>
    `;

    const targetGroup = document.getElementById(targetGroupId);
    if (targetGroup) {
      const itemsContainer = targetGroup.querySelector(".queue-group-items");
      if (itemsContainer) {
        itemsContainer.prepend(logItem); // Inserts into specific risk level container
      }
    } else {
      auditedReportsQueue.prepend(logItem); // Fallback if risk groups are not in HTML
    }
  }

  // ---- Loading state ----
  function setLoadingState(isLoading) {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.textContent = isLoading ? "Analyzing..." : "Run Baseline Analysis";

    if (isLoading) {
      resetResultBlock(resultBlocks.riskStatus, "Analysis in progress...");
    }
  }

  // Backend result rendering
  function renderBackendResult(data) {
    resetResultBlock(
      resultBlocks.riskStatus,
      `<strong>${data.classification}</strong> — ${data.transaction_count} transaction(s) analyzed.`
    );

    const signalCount = Array.isArray(data.signals) ? data.signals.length : 0;

    if (signalCount > 0) {
      const indicatorsList = data.signals.map(s => `<strong>${s.signal_type}</strong> [Severity: ${s.severity}]`);
      renderAsList(resultBlocks.riskIndicators, indicatorsList);

      const detailsList = data.signals.map(s => `<strong>${s.signal_type}</strong>: ${s.reason} <span style="color:#64748b;">(Transactions: ${s.transaction_ids.join(", ")})</span>`);
      renderAsList(resultBlocks.transactionsOfInterest, detailsList);
    } else {
      resetResultBlock(resultBlocks.riskIndicators, "No behavioral signals detected.");
      resetResultBlock(resultBlocks.transactionsOfInterest, "No transactions flagged.");
    }

    const b = data.baseline;
    if (b) {
      const baselineItems = [
        `<strong>History Strength:</strong> ${b.history_strength}`,
        `<strong>Volume:</strong> ${b.transaction_count} transactions over ${b.history_days} days`,
        `<strong>Typical Amount Range:</strong> ${b.amount_profile.typical_lower}–${b.amount_profile.typical_upper}`,
        `<strong>Primary Channel:</strong> ${b.channel_profile.dominant_channel}`,
        `<strong>Average Frequency:</strong> ~${b.frequency_profile.transactions_per_week ?? "N/A"} transactions/week`
      ];
      renderAsList(resultBlocks.customerBaseline, baselineItems);
    }

    resetResultBlock(
      resultBlocks.investigationSummary,
      `${signalCount} behavioral signal(s) detected. Overall classification: <strong>${data.classification}</strong>.`
    );

    if (Array.isArray(data.threads) && data.threads.length > 0) {
      const threadsList = data.threads.map(t => 
        `<strong>Thread ${t.thread_id}</strong> [Priority: ${t.priority}]<br/>` +
        `Timeframe: ${t.time_range.start} to ${t.time_range.end}<br/>` +
        `Associated Txns: ${t.transaction_ids.join(", ")} | Signals: ${t.signal_types.join(", ")}`
      );
      renderAsList(resultBlocks.investigatorPriority, threadsList);
    } else {
      resetResultBlock(resultBlocks.investigatorPriority, "No investigation threads identified.");
    }

    const currentFileName = fileInput.files[0] ? fileInput.files[0].name : "CSV Audit Session";
    const customerName = data.customer_name || data.customer_id || data.account_owner || null;
    
    appendAuditLogEntry(currentFileName, data.classification, signalCount, customerName);
  }

  function renderNarrative(narrative) {
    latestNarrative = narrative;
    const narrativeList = [
      `<strong>Assessment:</strong> ${narrative.assessment}`,
      `<strong>Key Findings:</strong> ${narrative.key_findings.join("; ")}`,
      `<strong>Behavioral Change:</strong> ${narrative.behavioral_change}`,
      `<strong>Investigator Priority:</strong> ${narrative.investigator_priority}`,
      `<strong>Recommended Actions:</strong> ${narrative.recommended_review.join("; ")}`
    ];
    renderAsList(resultBlocks.investigationSummary, narrativeList);
  }

  function renderError(message) {
    resetResultBlock(resultBlocks.riskStatus, `Unable to complete analysis: ${message}`);
  }

  // ---- Analyze Form Submit ----
  uploadForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (dataSource !== "file" || !fileInput.files[0]) {
      setFileStatus("Please select a CSV file before analyzing.", false);
      return;
    }  

    const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrfTokenElement) {
      renderError("CSRF token not found.");
      return;
    }

    const csrfToken = csrfTokenElement.value;
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    setLoadingState(true);

    fetch("/api/analyze/", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: formData,
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (!ok || data.status !== "success") {
          throw new Error(data.message || "Unexpected response from server.");
        }
        renderBackendResult(data);
      })
      .catch((error) => renderError(error.message))
      .finally(() => setLoadingState(false));
  });

  // ---- AI Narrative Generation ----
  generateReportBtn.addEventListener("click", () => {
    if (dataSource !== "file" || !fileInput.files[0]) {
      setFileStatus("Please select a CSV file before generating an AI report.", false);
      return;
    }
    
    const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrfTokenElement) {
      resetResultBlock(resultBlocks.investigationSummary, "AI report unavailable: CSRF token not found.");
      return;
    }

    const csrfToken = csrfTokenElement.value;
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    generateReportBtn.disabled = true;
    generateReportBtn.textContent = "Generating report...";

    fetch("/api/generate-report/", { 
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: formData 
    })
      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (!ok || data.status !== "success") {
          throw new Error(data.message || "Unable to generate report.");
        }
        renderNarrative(data.narrative);
      })
      .catch((error) => resetResultBlock(resultBlocks.investigationSummary, `AI report unavailable: ${error.message}`))
      .finally(() => {
        generateReportBtn.disabled = false;
        generateReportBtn.textContent = "Generate AI Narrative Analysis";
      });
  });

  // ---- PDF Generation ----
  generatePdfBtn.addEventListener("click", () => {
    if (dataSource !== "file" || !fileInput.files[0]) {
      setFileStatus("Please select a CSV file before downloading the PDF report.", false);
      return;
    }

    const csrfTokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrfTokenElement) {
      resetResultBlock(resultBlocks.investigationSummary, "PDF unavailable: CSRF token not found.");
      return;
    }

    const csrfToken = csrfTokenElement.value;
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    if (latestNarrative) {
      formData.append("narrative", JSON.stringify(latestNarrative));
    }

    generatePdfBtn.disabled = true;
    generatePdfBtn.textContent = "Preparing PDF...";

    fetch("/api/generate-pdf/", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.message || "Unable to generate PDF.");
          });
        }
        return response.blob();
      })
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "investigation_report.pdf";
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch((error) => resetResultBlock(resultBlocks.investigationSummary, `PDF unavailable: ${error.message}`))
      .finally(() => {
        generatePdfBtn.disabled = false;
        generatePdfBtn.textContent = "Download PDF Report";
      });
  });

  // ---- File Input Event ----
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) {
      dataSource = "file";
      setFileStatus(`Attached: ${file.name}`, true);
    } else {
      dataSource = null;
      setFileStatus("No file selected.", false);
    }
  });

  // ---- Sample Customer Trigger ----
  if (loadSampleBtn) {
    loadSampleBtn.addEventListener("click", () => {
      dataSource = "sample";
      setFileStatus("Sample customer selected.", false);
    });
  }

  // ---- Layout Interaction handlers ----
  if (toggleBaselineBtn && baselineDetailsPanel) {
    toggleBaselineBtn.addEventListener("click", () => {
      toggleBaselineBtn.classList.toggle("active");
      baselineDetailsPanel.classList.toggle("hidden");
    });
  }

  if (contactCustomerBtn && contactDrawer && closeDrawerBtn) {
    contactCustomerBtn.addEventListener("click", () => contactDrawer.classList.remove("hidden"));
    closeDrawerBtn.addEventListener("click", () => contactDrawer.classList.add("hidden"));
  }

  // Initial State Reset
  resetAllResults();
  setFileStatus("No file selected.", false);
});
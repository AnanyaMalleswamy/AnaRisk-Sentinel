
document.addEventListener("DOMContentLoaded", () => {
  // ---- Cache DOM elements ----
  const fileInput = document.getElementById("csv-file-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const loadSampleBtn = document.getElementById("load-sample-btn");
  const uploadForm = document.getElementById("upload-form");
  const generateReportBtn = document.getElementById("generate-report-btn");
  const generatePdfBtn = document.getElementById("generate-pdf-btn");
  let latestNarrative =null;

  const resultBlocks = {
    riskStatus: document.getElementById("risk-status"),
    riskIndicators: document.getElementById("risk-indicators"),
    transactionsOfInterest: document.getElementById("transactions-of-interest"),
    customerBaseline: document.getElementById("customer-baseline"),
    investigationSummary: document.getElementById("investigation-summary"),
    investigatorPriority: document.getElementById("investigator-priority"),
  };

  let dataSource = null;

  // ---- File status ----
  const fileStatus = document.createElement("p");
  fileStatus.id = "file-status";
  fileStatus.className = "placeholder-text";
  fileInput.insertAdjacentElement("afterend", fileStatus);

  function setFileStatus(message) {
    fileStatus.textContent = message;
  }

  // ---- Reset result blocks ----
  function resetResultBlock(block, message) {
    const text = block.querySelector(".placeholder-text");

    if (text) {
      text.textContent = message;
    }
  }

  function resetAllResults() {
    resetResultBlock(
      resultBlocks.riskStatus,
      "Analysis has not been run yet."
    );

    resetResultBlock(
      resultBlocks.riskIndicators,
      "Risk indicators will appear here after analysis."
    );

    resetResultBlock(
        resultBlocks.transactionsOfInterest,
        "Flagged transactions will appear here after analysis."
    );

    resetResultBlock(
      resultBlocks.investigatorPriority,
      "Suggested priority level will appear here after analysis."
    );

    resetResultBlock(
      resultBlocks.customerBaseline,
      "Baseline behavior summary will appear here after analysis."
    );

    resetResultBlock(
      resultBlocks.investigationSummary,
      "A summary of findings will appear here after analysis."
    );

    resetResultBlock(
      resultBlocks.investigatorPriority,
      "Suggested priority level will appear here after analysis."
    );
  }

  // ---- Loading state ----
  function setLoadingState(isLoading) {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.textContent = isLoading
      ? "Analyzing..."
      : "Analyze Transactions";

    if (isLoading) {
      resetResultBlock(
        resultBlocks.riskStatus,
        "Analysis in progress..."
      );
    }
  }

 
  // Backend result rendering
  function renderBackendResult(data) {
    resetResultBlock(
      resultBlocks.riskStatus,
      `${data.classification} — ${data.transaction_count} transaction(s) analyzed.`
    );

    if (Array.isArray(data.signals) && data.signals.length > 0) {
      const indicatorsText = data.signals
        .map((s) => `${s.signal_type} [${s.severity}]`)
        .join(", ");
      resetResultBlock(resultBlocks.riskIndicators, indicatorsText);

      const detailsText = data.signals
        .map((s) => `${s.signal_type}: ${s.reason} (Transactions: ${s.transaction_ids.join(", ")})`)
        .join(" | ");
      resetResultBlock(resultBlocks.transactionsOfInterest, detailsText);
    } else {
      resetResultBlock(resultBlocks.riskIndicators, "No behavioral signals detected.");
      resetResultBlock(resultBlocks.transactionsOfInterest, "No transactions flagged.");
    }

    const b = data.baseline;
    resetResultBlock(
      resultBlocks.customerBaseline,
      `History strength: ${b.history_strength} | ${b.transaction_count} transactions over ${b.history_days} days | ` +
      `Typical amount: ${b.amount_profile.typical_lower}–${b.amount_profile.typical_upper} | ` +
      `Usual channel: ${b.channel_profile.dominant_channel} | ~${b.frequency_profile.transactions_per_week ?? "N/A"} txns/week`
    );

    resetResultBlock(
      resultBlocks.investigationSummary,
      `${data.signals.length} behavioral signal(s) detected. Overall classification: ${data.classification}.`
    );
    if (Array.isArray(data.threads) && data.threads.length > 0) {
        const threadsText = data.threads
    .map((t) => {
      const signalList = t.signal_types.join(", ");

      return `${t.thread_id} [Priority: ${t.priority}] ${t.time_range.start} to ${t.time_range.end} — ` +
             `Transactions: ${t.transaction_ids.join(", ")} — Signals: ${signalList}`;
    })
    .join(" | ");

    resetResultBlock(
        resultBlocks.investigatorPriority,
        `Investigation Threads: ${threadsText}`
    );
    } else {
    resetResultBlock(
        resultBlocks.investigatorPriority,
        "No investigation threads identified."
    );
    }
}

function renderNarrative(narrative) {
    latestNarrative = narrative; // Store the latest narrative for potential future use
    const lines = [
      `Assessment: ${narrative.assessment}`,
      `Key findings: ${narrative.key_findings.join(" | ")}`,
      `Behavioral change: ${narrative.behavioral_change}`,
      `Investigator priority: ${narrative.investigator_priority}`,
      `Recommended review: ${narrative.recommended_review.join(" | ")}`,
    ];
    resetResultBlock(resultBlocks.investigationSummary, lines.join(" — "));
    }

  // ---- Render error ----
  function renderError(message) {
    resetResultBlock(
      resultBlocks.riskStatus,
      `Unable to complete analysis: ${message}`
    );
  }

  // ---- Analyze Transactions ----
  uploadForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (dataSource !== "file" || !fileInput.files[0]) {
      setFileStatus("Please select a CSV file before analyzing.");
      return;
    }  

    const csrfTokenElement = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    );

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
      headers: {
        "X-CSRFToken": csrfToken,
      },
      body: formData,
    })
      .then((response) =>
        response.json().then((data) => ({
          ok: response.ok,
          data,
        }))
      )
      .then(({ ok, data }) => {
        if (!ok || data.status !== "success") {
          throw new Error(
            data.message || "Unexpected response from server."
          );
        }

        renderBackendResult(data);
      })
      .catch((error) => {
        renderError(error.message);
      })
      .finally(() => {
        setLoadingState(false);
      });

/* ---- Event: Generate Investigation Report (separate, explicit Gemini call) ---- */
    generateReportBtn.addEventListener("click", () => {
    if (dataSource !== "file" || !fileInput.files[0]) {
      setFileStatus("Please select a CSV file (not the sample) before generating an AI report.");
      return;
    }
     const csrfTokenElement = document.querySelector(
    "[name=csrfmiddlewaretoken]"
  );

  if (!csrfTokenElement) {
    resetResultBlock(
      resultBlocks.investigationSummary,
      "AI report unavailable: CSRF token not found."
    );
    return;
  }
   

    const csrfToken = csrfTokenElement.value;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    generateReportBtn.disabled = true;
    generateReportBtn.textContent = "Generating report...";

    fetch("/api/generate-report/", { method: "POST",
        headers:{
            "X-CSRFToken": csrfToken,} 
        ,body: formData })

      .then((response) => response.json().then((data) => ({ ok: response.ok, data })))
      .then(({ ok, data }) => {
        if (!ok || data.status !== "success") {
          throw new Error(data.message || "Unable to generate report.");
        }
        renderNarrative(data.narrative);
      })
      .catch((error) => {
        resetResultBlock(resultBlocks.investigationSummary, `AI report unavailable: ${error.message}`);
      })
      .finally(() => {
        generateReportBtn.disabled = false;
        generateReportBtn.textContent = "Generate Investigation Report";
      });
    });  

  });

   generatePdfBtn.addEventListener("click", () => {
    if (dataSource !== "file" || !fileInput.files[0]) {
        setFileStatus(
            "Please select a CSV file before downloading the PDF report."
        );
        return;
    }

    const csrfTokenElement = document.querySelector(
        "[name=csrfmiddlewaretoken]"
    );

    if (!csrfTokenElement) {
        resetResultBlock(
            resultBlocks.investigationSummary,
            "PDF unavailable: CSRF token not found."
        );
        return;
    }

    const csrfToken = csrfTokenElement.value;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    if (latestNarrative) {
    formData.append(
        "narrative",
        JSON.stringify(latestNarrative)
    );
}

    generatePdfBtn.disabled = true;
    generatePdfBtn.textContent = "Preparing PDF...";

    fetch("/api/generate-pdf/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken,
        },
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                return response.json().then((data) => {
                    throw new Error(
                        data.message || "Unable to generate PDF."
                    );
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
        .catch((error) => {
            resetResultBlock(
                resultBlocks.investigationSummary,
                `PDF unavailable: ${error.message}`
            );
        })
        .finally(() => {
            generatePdfBtn.disabled = false;
            generatePdfBtn.textContent = "Download PDF Report";
        });
});

  // ---- File selected ----
  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (file) {
      dataSource = "file";
      setFileStatus(`Selected file: ${file.name}`);
    } else {
      dataSource = null;
      setFileStatus("No file selected.");
    }
  });

  // ---- Sample customer ----
  if (loadSampleBtn) {
    loadSampleBtn.addEventListener("click", () => {
      dataSource = "sample";
      setFileStatus(
        "Sample customer selected. Please use a CSV file for Phase 7 parsing."
      );
    });
  }

  // ---- Initial state ----
  resetAllResults();
  setFileStatus("No file selected.");
});


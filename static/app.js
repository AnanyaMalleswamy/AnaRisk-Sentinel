javascript
document.addEventListener("DOMContentLoaded", () => {
  // ---- Cache DOM elements ----
  const fileInput = document.getElementById("csv-file-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const loadSampleBtn = document.getElementById("load-sample-btn");
  const uploadForm = document.getElementById("upload-form");

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

  // ---- Render backend result ----
  function renderBackendResult(data) {
    resetResultBlock(
      resultBlocks.riskStatus,
      `Parsed successfully — ${data.transaction_count} transaction(s) found.`
    );

    if (Array.isArray(data.preview) && data.preview.length > 0) {
      const previewText = data.preview
        .map(
          (transaction) =>
            `${transaction.transaction_id}: ${transaction.amount} (${transaction.channel})`
        )
        .join(" | ");

      resetResultBlock(
        resultBlocks.transactionsOfInterest,
        previewText
      );
    } else {
      resetResultBlock(
        resultBlocks.transactionsOfInterest,
        "No transactions to preview."
      );
    }

    resetResultBlock(
      resultBlocks.riskIndicators,
      "Risk calculation not implemented in this phase."
    );

    resetResultBlock(
      resultBlocks.customerBaseline,
      "Baseline calculation not implemented in this phase."
    );

    resetResultBlock(
      resultBlocks.investigationSummary,
      "CSV parsing verified. Investigation summary not implemented in this phase."
    );
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


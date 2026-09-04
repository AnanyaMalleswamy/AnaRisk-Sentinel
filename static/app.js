 
document.addEventListener("DOMContentLoaded", () => {
 
  /* ---- Cache DOM elements ---- */
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

  const fileStatus = document.createElement("p");
  fileStatus.id = "file-status";
  fileStatus.className = "placeholder-text";
  fileInput.insertAdjacentElement("afterend", fileStatus);
 
  function setFileStatus(message) {
    fileStatus.textContent = message;
  }
 
  /* ---- Reset a result block back to its original placeholder text ---- */
  function resetResultBlock(block, message) {
    const text = block.querySelector(".placeholder-text");
    if (text) {
      text.textContent = message;
    }
  }
  
function resetAllResults() {
    resetResultBlock(resultBlocks.riskStatus, "Analysis has not been run yet.");
    resetResultBlock(resultBlocks.riskIndicators, "Risk indicators will appear here after analysis.");
    resetResultBlock(resultBlocks.transactionsOfInterest, "Flagged transactions will appear here after analysis.");
    resetResultBlock(resultBlocks.customerBaseline, "Baseline behavior summary will appear here after analysis.");
    resetResultBlock(resultBlocks.investigationSummary, "A summary of findings will appear here after analysis.");
    resetResultBlock(resultBlocks.investigatorPriority, "Suggested priority level will appear here after analysis.");
  }
 
  /* ---- Loading state (reusable in Phase 4 when a real request is added) ---- */
  function setLoadingState(isLoading) {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.textContent = isLoading ? "Analyzing..." : "Analyze Transactions";
 
    if (isLoading) {
      resetResultBlock(resultBlocks.riskStatus, "Analysis in progress...");
    }
  }

  /* ---- Backend result rendering ---- */
  function renderBackendResult(message) {
    const text = resultBlocks.riskStatus.querySelector(".placeholder-text");
    if (text) {
      text.textContent = message;
    }
  }

  function renderError(message) {
    const text = resultBlocks.riskStatus.querySelector(".placeholder-text");
    if (text) {
      text.textContent = `Unable to complete analysis: ${message}`;
    }
  }

  /* ---- Event: Analyze Transactions ---- */
  uploadForm.addEventListener("submit", (event) => {
    event.preventDefault(); // handled entirely via fetch below, not a page submit

    if (!dataSource) {
      setFileStatus("Please select a CSV file or load the sample customer before analyzing.");
      return;
    }

    setLoadingState(true);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch("/api/analyze/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Server responded with status ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.status !== "success" || !data.message) {
          throw new Error("Unexpected response from server.");
        }
        renderBackendResult(data.message);
      })
      .catch((error) => {
        renderError(error.message);
      })
      .finally(() => {
        setLoadingState(false);
      });
  });

 
  /* ---- Event: file selected ---- */
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
  /* ---- Initial state ---- */
  resetAllResults();
  setFileStatus("No file selected.");
});  
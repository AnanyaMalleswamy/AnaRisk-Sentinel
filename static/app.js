 
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

/* ---- State ---- */
  // dataSource is null, "file", or "sample" — tracks whether Analyze has
  // something to work with, without ever holding real parsed data.
  let dataSource = null;
 
  /* ---- Small helper: a status line under the file input, created here
     so no HTML changes are required. Reused for filename + messages. ---- */
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

/* ---- Mock result rendering ---- */
  function renderMockResults() {
    const text = resultBlocks.riskStatus.querySelector(".placeholder-text");
    if (text) {
      text.textContent =
        "Demo Result — Analysis pipeline is connected to the frontend. " +
        "Backend integration will be added in the next phase.";
    }
 
    const mockNote = "Pipeline connected (mock data placeholder — no backend result yet).";
    resetResultBlock(resultBlocks.riskIndicators, mockNote);
    resetResultBlock(resultBlocks.transactionsOfInterest, mockNote);
    resetResultBlock(resultBlocks.customerBaseline, mockNote);
    resetResultBlock(resultBlocks.investigationSummary, mockNote);
    resetResultBlock(resultBlocks.investigatorPriority, mockNote);
  }
 
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
 
  /* ---- Event: Load Sample Customer ---- */
  loadSampleBtn.addEventListener("click", () => {
    dataSource = "sample";
    fileInput.value = ""; // clear any chosen file so state stays unambiguous
    setFileStatus("Sample customer selected (demo data — not a real record).");
  });
 
  /* ---- Event: Analyze Transactions ---- */
  uploadForm.addEventListener("submit", (event) => {
    event.preventDefault(); // no network request; this is a local mock action
 
    if (!dataSource) {
      setFileStatus("Please select a CSV file or load the sample customer before analyzing.");
      return;
    }
 
    setLoadingState(true);
 
    // Simulated delay so the loading state is visible and reusable later
    // when Phase 4 replaces this with a real request.
    setTimeout(() => {
      setLoadingState(false);
      renderMockResults();
    }, 900);
  });
 
  /* ---- Initial state ---- */
  resetAllResults();
  setFileStatus("No file selected.");
});  
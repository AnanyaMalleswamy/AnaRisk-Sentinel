 
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
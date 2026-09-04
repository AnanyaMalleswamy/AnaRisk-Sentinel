 
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
    
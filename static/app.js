 
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
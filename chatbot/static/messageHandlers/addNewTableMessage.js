import { scrollToBottom } from "../utils/index.js";

export function addNewTableMessage(message, sender) {
  const messageElement = document.createElement("li");

  messageElement.classList.add(sender);
  const tableContainer = document.createElement("div");
  tableContainer.classList.add("table-container");

  const rows = message.split("\n").filter((row) => row.trim() !== "");
  const table = document.createElement("table");
  table.classList.add("chat-table");

  rows.forEach((row, index) => {
    const tr = document.createElement("tr");
    const cells = row
      .split("|")
      .map((cell) => cell.trim())
      .filter((cell) => cell !== ""); // Split columns

    cells.forEach((cell, cellIndex) => {
      const td = document.createElement(index === 0 ? "th" : "td");
      td.textContent = cell;

      if (index === 1) {
        td.style.borderBottom = "2px solid #ccc";
      }

      tr.appendChild(td);
    });

    table.appendChild(tr);
  });

  tableContainer.appendChild(table);
  messageElement.appendChild(tableContainer);

  document.getElementById("messages").appendChild(messageElement);
  scrollToBottom();
}

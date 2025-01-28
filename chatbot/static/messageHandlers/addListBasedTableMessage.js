export function addListBasedTableMessage(data, sender) {
  const container = document.getElementById("messages");
  const messageElement = document.createElement("li");
  messageElement.classList.add(
    sender === "agent" ? "agent-message" : "user-message",
    "message-margin"
  );

  let tableHtml = "<table class='chat-table'>";
  tableHtml +=
    "<thead><tr><th>Category</th><th>Amount (Rupees)</th></tr></thead>";
  tableHtml += "<tbody>";
  data.forEach((row) => {
    tableHtml += `<tr><td>${row.key}</td><td>${row.value}</td></tr>`;
  });
  tableHtml += "</tbody></table>";

  messageElement.innerHTML = tableHtml;
  container.appendChild(messageElement);
}

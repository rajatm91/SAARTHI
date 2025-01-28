export function addTableMessage(rows) {
    const messages = document.getElementById("messages");
    if (messages) {
      const newMessage = document.createElement("li");
      newMessage.classList.add("agent");
  
      // Create table element
      const table = document.createElement("table");
      table.style.borderCollapse = "collapse";
      table.style.width = "100%";
  
      // Add table header
      const headerRow = document.createElement("tr");
      const header1 = document.createElement("th");
      const header2 = document.createElement("th");
      header1.textContent = "Month";
      header2.textContent = "Amount";
      header1.style.border = "1px solid #ddd";
      header2.style.border = "1px solid #ddd";
      header1.style.padding = "8px";
      header2.style.padding = "8px";
      header1.style.textAlign = "left";
      header2.style.textAlign = "left";
      headerRow.appendChild(header1);
      headerRow.appendChild(header2);
      table.appendChild(headerRow);
  
      // Add rows to the table
      rows.forEach((row) => {
        const tableRow = document.createElement("tr");
        const cell1 = document.createElement("td");
        const cell2 = document.createElement("td");
        cell1.textContent = row.key;
        cell2.textContent = row.value;
        cell1.style.border = "1px solid #ddd";
        cell2.style.border = "1px solid #ddd";
        cell1.style.padding = "8px";
        cell2.style.padding = "8px";
        tableRow.appendChild(cell1);
        tableRow.appendChild(cell2);
        table.appendChild(tableRow);
      });
  
      // Append the table to the message
      newMessage.appendChild(table);
      messages.appendChild(newMessage);
    } else {
      console.error("Messages container not found!");
    }
  }
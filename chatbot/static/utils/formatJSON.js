export function formatJSON(json) {
    const container = document.createElement("div");
  
    if (Array.isArray(json)) {
      json.forEach((item, index) => {
        const itemDiv = document.createElement("div");
        itemDiv.classList.add("json-item");
        itemDiv.innerHTML = `<strong>[${index}]</strong>: ${
          typeof item === "object" ? "" : item
        }`;
  
        if (typeof item === "object") {
          const nestedContent = formatJSON(item);
          itemDiv.appendChild(nestedContent);
        }
  
        container.appendChild(itemDiv);
      });
    } else {
      Object.entries(json).forEach(([key, value]) => {
        const itemDiv = document.createElement("div");
        itemDiv.classList.add("json-item");
        itemDiv.innerHTML = `<strong>${key}:</strong> ${
          typeof value === "object" ? "" : value
        }`;
  
        if (typeof value === "object") {
          const nestedContent = formatJSON(value);
          itemDiv.appendChild(nestedContent);
        }
  
        container.appendChild(itemDiv);
      });
    }
  
    return container;
  }
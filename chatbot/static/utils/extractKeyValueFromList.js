export function extractKeyValueFromList(messageContent) {
    const lines = messageContent.split("\n");
    const data = [];
  
    lines.forEach((line) => {
      if (line.includes(":")) {
        const [key, value] = line.split(":");
        data.push({ key: key.replace("-", "").trim(), value: value.trim() });
      }
    });
  
    return data;
  }
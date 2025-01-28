import { parseConcatenatedJSON } from "../utils/parseConcatenatedJSON.js";
import { addNewTableMessage } from "./addNewTableMessage.js";
import { addServerMessage } from "./addServerMessage.js";
import { toggleLoadingIndicator } from "./toggleLoadingIndicator.js";
import { extractKeyValueFromList } from "../utils/extractKeyValueFromList.js";
import { addListBasedTableMessage } from "./addListBasedTableMessage.js";
import { addTableMessage } from "./addTableMessage.js";
import { addImageMessage } from "./addImageMessage.js";
import { addMessage } from "./addMessage.js";
import { extractImagePath, isJsonObject } from "../utils/index.js";

export function handleMessage(data) {
  toggleLoadingIndicator(true);
  setTimeout(() => {
    addServerMessage(JSON.stringify(data));
    if (
      data &&
      data?.type !== "tool_response" &&
      data.content &&
      data.content.content
    ) {
      const messageContent = data.content.content.trim();
      const imagePath = extractImagePath(data.content.content);
      const finalAnswer =
        parseConcatenatedJSON(data?.content?.content)?.[0]?.final_answer ||
        null;
      if (messageContent.includes("|") && messageContent.includes("---")) {
        addNewTableMessage(messageContent, "agent");
      } else if (
        messageContent.includes(
          "The total spend across different categories is as follows:"
        )
      ) {
        const tableData = extractKeyValueFromList(messageContent);
        addListBasedTableMessage(tableData, "agent");
      } else if (messageContent.includes("Here is the analysis")) {
        // Extract and format the table data
        const rows = messageContent
          .split("\n")
          .filter((line) => line.includes(":")) // Filter lines with data
          .map((line) => {
            const [key, value] = line.split(":");
            return { key: key.trim(), value: value.trim() };
          });

        // Display the data in tabular format
        addTableMessage(rows);
      } else if (imagePath) {
        // If image path is present, display the image in the chat
        addImageMessage(imagePath);
      } else if (
        messageContent &&
        messageContent !== "TERMINATE" &&
        typeof messageContent === "string" &&
        !isJsonObject(messageContent) &&
        finalAnswer
      ) {
        addMessage(finalAnswer, "agent");
      } else if (
        messageContent &&
        data?.content?.sender_name !== "user_proxy"
      ) {
        addMessage(messageContent, "agent");
      } else {
        console.log("Invalid or terminate message:", messageContent);
      }
    }
    toggleLoadingIndicator(false);
  }, [2000]);
}

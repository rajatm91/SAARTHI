export function parseConcatenatedJSON(concatenatedJSON) {
    try {
      // Split the string into separate JSON objects
      const jsonObjects = concatenatedJSON?.trim()?.split("\n");
  
      // console.log('JSON OBJECT',jsonObjects)
      // Parse each JSON string into an object
      const parsedObjects = jsonObjects?.map((jsonStr) => JSON.parse(jsonStr));
  
      return parsedObjects;
    } catch (error) {
      // console.error("Error parsing concatenated JSON:", error);
      return [];
    }
  }
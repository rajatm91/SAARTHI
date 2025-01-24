html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAARTHI: Smart AI Agent</title>
    <link rel="stylesheet" href="chatbot/static/styles.css">
</head>
<body>
<div class="chat-container">
    <div class="title">SAARTHI: Smart AI Agent for Real-Time Handling & Insights</div>
    <ul id="messages" class="messages"></ul>
    <div class="input-area">
        <input type="text" id="messageText" placeholder="Type a message..." autocomplete="off"/>
        <button onclick="sendMessage()">Send</button>
    </div>
</div>
<script src="chatbot/static/script.js"></script>
</body>
</html>
"""
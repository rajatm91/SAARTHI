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

    <!-- Main screen and Server messages -->
    <div id="main-screen" class="container">
        <!-- Left part: User chat -->
        <div class="chat-container left">
            <div class="title">SAARTHI: Smart AI Agent</div>
            <ul id="messages" class="messages"></ul>
            <div id="loading-indicator" style="display: none;">
                <span>Agent is typing<span id="dots">...</span></span>
            </div>

            <div class="input-area">
                <input type="text" id="messageText" placeholder="Type a message..." autocomplete="off" />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <!-- Right part: Server messages and View Registry button -->
        <div class="chat-container right">
            <div class="header">
                <div class="title">Server Messages</div>
                <button class="registry-button" onclick="window.location.href='/chatbot/static/registry.html'">View
                    Registry</button>
            </div>
            <div id="server-messages" class="message-container"></div>
        </div>
    </div>
    
    <script type="module" src="chatbot/static/script.js"></script>
</body>

</html>

"""
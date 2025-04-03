# app.py
import gradio as gr
from utils.model_handler import generate_code
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

custom_css = """
:root {
    --gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
}

/* Chat bubbles */
.dark .user, .dark .assistant {
    color: white !important;
}

.user {
    background: #4f46e5 !important;
    border-radius: 20px 20px 4px 20px !important;
    margin-left: auto !important;
    max-width: 80%;
    animation: slideInRight 0.3s ease-out;
}

.assistant {
    background: #3730a3 !important;
    border-radius: 20px 20px 20px 4px !important;
    margin-right: auto !important;
    max-width: 80%;
    animation: slideInLeft 0.3s ease-out;
}

@keyframes slideInRight {
    from { transform: translateX(20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideInLeft {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Typing animation */
.typing-indicator {
    display: inline-flex;
    gap: 4px;
    padding: 12px;
    background: #3730a3 !important;
    border-radius: 20px;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background: rgba(255,255,255,0.6);
    border-radius: 50%;
    animation: typing-dot 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-dot {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-6px); }
}

/* Input area */
.dark .input-box {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
}

.send-btn {
    transition: transform 0.2s ease !important;
}

.send-btn:hover {
    transform: translateY(-2px) scale(1.05);
}

.stop-btn {
    background: #dc2626 !important;
    border-color: #dc2626 !important;
}

.stop-btn:hover {
    background: #b91c1c !important;
    transform: scale(0.98) !important;
}

/* Sidebar styling */
.sidebar {
    background: var(--gradient) !important;
    padding: 1.5rem !important;
    border-radius: 0 16px 16px 0 !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.1);
}

.sidebar .button {
    width: 100%;
    margin: 8px 0 !important;
    justify-content: center !important;
}

.logo-container {
    text-align: center;
    margin-bottom: 2rem;
}

.logo {
    width: 60px;
    height: 60px;
    margin-bottom: 1rem;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

.loading-spinner {
    animation: spin 1s linear infinite;
    width: 24px;
    height: 24px;
    margin-left: 8px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Code syntax highlighting */
pre code.hljs {
    padding: 1rem !important;
    border-radius: 12px !important;
    background: #1e1e1e !important;
}

.dark .hljs {
    color: #d4d4d4 !important;
}

.hljs-keyword { color: #569CD6; }
.hljs-built_in { color: #4EC9B0; }
.hljs-string { color: #CE9178; }
.hljs-function { color: #DCDCAA; }
.hljs-params { color: #9CDCFE; }
.hljs-comment { color: #6A9955; }
"""

def format_history(messages):
    formatted = []
    for msg in messages:
        if msg["role"] == "user":
            formatted.append((msg["content"], None))
        else:
            content = msg["content"]
            parts = content.split("```")
            new_content = ""
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Code block
                    lang_match = next((l for l in ["python", "javascript", "java", "c++", "rust", "go"]
                                     if part.lower().startswith(l)), "")
                    if lang_match:
                        try:
                            code_content = part.split("\n", 1)[1]
                            lexer = get_lexer_by_name(lang_match, stripall=True)
                            formatter = HtmlFormatter(style="monokai", noclasses=True)
                            highlighted = highlight(code_content, lexer, formatter)
                            new_content += f"<pre>{highlighted}</pre>"
                        except Exception:
                            new_content += f"<pre>{part}</pre>"
                    else:
                        new_content += f"<pre>{part}</pre>"
                else:
                    new_content += part  # Plain text

            if formatted and formatted[-1][1] is None:
                formatted[-1] = (formatted[-1][0], new_content)
            else:
                formatted.append((None, new_content))
    return formatted


def respond(message, chat_history, language, temperature, cancel_flag):
    try:
        cancel_flag[0] = False  # Reset cancellation flag
        formatted_history = [
            {"role": "user" if who else "assistant", "content": content}
            for entry in chat_history
            for content, who in [(entry[0], True), (entry[1], False)]
            if content is not None
        ]
        
        formatted_history.append({"role": "user", "content": message})
        
        # Add typing indicator
        formatted_history.append({
            "role": "assistant", 
            "content": """<div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>"""
        })
        
        yield format_history(formatted_history), "", gr.Button(visible=False), gr.Button(visible=True)
        formatted_history.pop()
        
        full_response = ""
        # Pass cancellation flag to generate_code
        for chunk in generate_code(message, language, temperature, cancel_flag):
            if cancel_flag[0]:
                formatted_history.append({"role": "assistant", "content": "⏹️ Generation stopped."})
                yield format_history(formatted_history), "", gr.Button(visible=True), gr.Button(visible=False)
                return

            full_response += chunk
            formatted_history.append({"role": "assistant", "content": full_response})
            yield format_history(formatted_history), "", gr.Button(visible=False), gr.Button(visible=True)
            formatted_history.pop()

        
        formatted_history.append({"role": "assistant", "content": full_response})
        yield format_history(formatted_history), "", gr.Button(visible=True), gr.Button(visible=False)
        
    except Exception as e:
        formatted_history.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
        yield format_history(formatted_history), "", gr.Button(visible=True), gr.Button(visible=False)

def cancel_generation(cancel_flag):
    cancel_flag[0] = True
    return [True]


def new_chat():
    return [], "", [False], gr.Button(visible=True), gr.Button(visible=False)

with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="purple"),
    css=custom_css,
    title="CodeGen AI"
) as demo:
    cancel_flag = gr.State([False])
    gr.HTML("<link rel='icon' href='./static/images/deepseek-icon.jpeg'>")
    
    with gr.Row():
        with gr.Column(scale=1, elem_classes=["sidebar"]):
            gr.Markdown("""
            <div class="logo-container">
                <img src="https://i.ibb.co/3zt7PVx/spinner.png" class="logo"/>
                <h3 style="color: white; margin: 0;">CodeGen Pro</h3>
            </div>
            """)
            
            new_chat_btn = gr.Button("🔄 New Chat", variant="secondary")
            gr.Markdown("---")
            gr.Markdown("**Settings**")
            language = gr.Dropdown(
                ["Python", "JavaScript", "Java", "C++", "Rust", "Go"],
                value="Python",
                label="Programming Language"
            )
            temperature = gr.Slider(
                0.1, 1.0, value=0.7,
                label="Creativity Level",
                info="Lower = More Factual, Higher = More Creative"
            )
            gr.Markdown("---")
            gr.Markdown("📖 [Documentation](https://example.com)  \n📩 [Support](mailto:support@example.com)")

        with gr.Column(scale=4):
            gr.Markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h1 style="font-size: 2.5rem; margin: 0; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    🚀 CodeGen Pro
                </h1>
            </div>
            """)
            
            chatbot = gr.Chatbot(
                elem_classes=["chat-container"],
                avatar_images=(
                    ("https://img.icons8.com/?size=100&id=kDoeg22e5jUY&format=png&color=000000", "user"),
                    ("https://img.icons8.com/?size=100&id=THRPlyXrzBJk&format=png&color=000000", "assistant")
                ),
                height="70vh",
                show_label=False
            )
            
            with gr.Row(elem_classes=["input-box"]):
                with gr.Column(scale=4):
                    msg = gr.Textbox(
                        placeholder="Describe the code you want to generate...",
                        show_label=False,
                        container=False
                    )
                with gr.Column(scale=1):
                    btn = gr.Button("Generate Code", variant="primary", elem_classes=["send-btn"], visible=True)
                    stop_btn = gr.Button("⏹ Stop", variant="stop", elem_classes=["stop-btn"], visible=False)

    msg.submit(
        respond,
        [msg, chatbot, language, temperature, cancel_flag],
        [chatbot, msg, btn, stop_btn],
    )
    btn.click(
        respond,
        [msg, chatbot, language, temperature, cancel_flag],
        [chatbot, msg, btn, stop_btn],
    )
    stop_btn.click(
    fn=cancel_generation,
    inputs=[cancel_flag],
    outputs=[cancel_flag],
    queue=False
)

    new_chat_btn.click(
        new_chat,
        outputs=[chatbot, msg, cancel_flag, btn, stop_btn]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        favicon_path="favicon.ico",
        show_error=True
    )
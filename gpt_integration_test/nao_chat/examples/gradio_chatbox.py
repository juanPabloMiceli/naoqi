"""
From gradio's https://gradio.app/creating-a-chatbot/ guide

You'll notice that when a user submits their message, we now chain two event
events with .then():

 -The first method user() updates the chatbot with the user message and clears
  the input field. Because we want this to happen instantly, we set
  queue=False, which would skip any queue if it had been enabled.
  The chatbot's history is appended with (user_message, None), the None
  signifying that the bot has not responded.

 -The second method, bot() updates the chatbot history with the bot's response.
  Instead of creating a new message, we just replace the previously-created
  None message with the bot's response. Finally, we construct the message
  character by character and yield the intermediate outputs as they are being
  constructed. Gradio automatically turns any function with the yield keyword
  into a streaming output interface.

Of course, in practice, you would replace bot() with your own more complex
function, which might call a pretrained model or an API, to generate a
response.

Finally, we enable queuing by running demo.queue(), which is required for
streaming intermediate outputs. You can try the improved chatbot by scrolling
to the demo at the top of this page.
"""

import gradio as gr
import time

from nao_chat.chatbot import ChatBotManager
from nao_chat.conversation_pipe import ConversationPipe

convo_pipe = ConversationPipe()
convo_pipe.clear()

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user_message_arrived(user_message: gr.Textbox, history: gr.Chatbot):
        convo_pipe.add_user_message(user_message)
        return "", history + [[user_message, None]]

    def wait_for_bot_message(history):
        history[-1][1] = " "
        while not convo_pipe.get_bot_message_availability():
            for _ in range(3):
                history[-1][1] += "."
                yield history
                time.sleep(1)
            history[-1][1] = " "
            yield history

        bot_message = convo_pipe.get_bot_message()

        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.05)
            yield history

    msg.submit(user_message_arrived, [msg, chatbot], [msg, chatbot], queue=False).then(
        wait_for_bot_message, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=7860, prevent_thread_lock=True)
cbm = ChatBotManager()
cbm.chatbox = demo
cbm.start_chat("gradio")

import gradio as gr

demo = gr.Interface(fn=lambda name: f"Hello {name}!", inputs="text", outputs="text")
demo.launch(server_name="0.0.0.0", server_port=7860)
# to run locally, server name MUST be "0.0.0.0"

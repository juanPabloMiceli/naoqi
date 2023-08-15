# nao_chat

nao_chat is a virtual assistant chatbot for a dental clinic

## How to test nao_chat

1. Run build.sh file from nao_chat/ to build the image
2. Run run.sh file from nao_chat/ to run the container
3. Once inside the container run: poetry run python nao_chat/main.py --mode
The mode can be cli or nao

### Tips for making good tests on nao_chat

1. Important: you must wait until nao_chat finishes writing to send a message!
2. Write the dates in the following format: "YYYY-MM-DD"

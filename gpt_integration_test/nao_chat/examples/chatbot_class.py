from nao_chat.chatbot import ChatBot

test_prompt = "You are a firendly chatbot that's hellping test a chatbot tool I made."

test_chatbot = ChatBot("test_chatbot", test_prompt)

test_chatbot.add_message("How are you?")


test_chatbot.run_conversation()

test_chatbot.reset_conversation()

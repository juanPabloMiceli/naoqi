from workspace.external_modules.chat.nao_chat.chatbot import ChatBotManager


if __name__ == "__main__":
    cbm = ChatBotManager()
    # start chat in NAO mode
    cbm.start_chat("nao")

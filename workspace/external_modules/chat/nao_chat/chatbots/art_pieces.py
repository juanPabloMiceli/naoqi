from workspace.external_modules.chat.nao_chat.enums import (
    AvailableChatbots,
    ChatRoles,
    ArtPiece,
)
from workspace.external_modules.chat.nao_chat.chatbot import ChatBot
from workspace.external_modules.chat.nao_chat.cfg import PROMPT_STORE_PATH
from workspace.external_modules.chat.nao_chat.helpers import read_text_file


prompt = read_text_file(f"{PROMPT_STORE_PATH}/art_pieces.txt")

ART_PIECES = ChatBot("ART_PIECES", base_prompt=prompt)


@ART_PIECES.add_handler(
    openai_function_dict={
        "name": "redirect",
        "description": "Redirect the conversation to the appropiate chatbot",
        "parameters": {
            "type": "object",
            "properties": {
                "bot": {
                    "type": "string",
                    "enum": [bot.value for bot in AvailableChatbots],
                    "description": "The bot name to redirect to",
                },
            },
            "required": ["bot"],
        },
    },
    parsing_functions={"bot": lambda x: x},
)
def redirect(chatbot: ChatBot, bot: str):
    chatbot.manager.redirect(bot)


@ART_PIECES.add_handler(
    openai_function_dict={
        "name": "displayed_art_pieces",
        "description": "Show currently displayed art pieces",
        "parameters": {
            "type": "object",
            "properties": {
                "artist": {
                    "type": "string",
                    "description": "The name of an artist to which filter the art pieces",
                },
            },
        },
    },
    parsing_functions={
        "artist": lambda x: x,
    },
)
def displayed_art_pieces(chatbot: ChatBot, artist: str = None):
    message = "The currently displayed art pieces are:\n"

    art_pieces = [art_piece.value for art_piece in ArtPiece]

    # filter art_pieces by artist
    if artist is not None:
        art_pieces = [art_piece for art_piece in art_pieces if artist]

    for art_piece in art_pieces:
        message += f" - {art_piece.capitalize().replace('_', ' ')}"

    chatbot.add_message(message, ChatRoles.function, function="displayed_art_pieces")
    chatbot.run_conversation()


@ART_PIECES.add_handler(
    openai_function_dict={
        "name": "is_displayed",
        "description": "Tell an user if a particular art piece is being displayed or not",
        "parameters": {
            "type": "object",
            "properties": {
                "art_piece": {
                    "type": "string",
                    "description": "An art piece the user would like to know if it is being displayed at the museum",
                },
            },
            "required": ["art_piece"],
        },
    },
    parsing_functions={
        "art_piece": lambda x: x,
    },
)
def is_displayed(chatbot: ChatBot, art_piece: str):
    try:
        ArtPiece(art_piece)
        is_displayed = True
    except ValueError:
        is_displayed = False

    if is_displayed:
        message = f"{art_piece} is being displayed at the museum"
    else:
        message = f"{art_piece} is not being displayed at the museum"

    chatbot.add_message(message, ChatRoles.function, function="payment_methods")
    chatbot.run_conversation()


@ART_PIECES.add_handler(
    openai_function_dict={
        "name": "guide",
        "description": "Guide an user to the requested art piece location",
        "parameters": {
            "type": "object",
            "properties": {
                "art_piece": {
                    "type": "string",
                    "description": "An art piece the user want to be guided to",
                },
            },
            "required": ["art_piece"],
        },
    },
    parsing_functions={
        "art_piece": lambda x: str,
    },
)
def guide(chatbot: ChatBot, art_piece: str):
    try:
        ArtPiece(art_piece)
        # locate art piece
        position = (0, 0)  # QR_LOCATION[art_piece]
        # execute_move_mission_on_nao(position)
        print(f"Mission: Move to {position}")

        message = "We've reached art piece location"

    except ValueError:
        message = f"{art_piece} is not being displayed at the museum."

    chatbot.add_message(message, ChatRoles.function, function="guide")
    chatbot.run_conversation()

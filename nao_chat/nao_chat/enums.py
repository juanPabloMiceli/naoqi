from enum import Enum


class ChatRoles(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    function = "function"


class AvailableChatbots(Enum):
    small_talk = "SMALL_TALK"
    appointments = "ART_PIECES"
    information = "INFORMATION"


class OpenAIModel(Enum):
    gpt4 = "gpt-4"
    gpt3 = "gpt-3.5-turbo"
    gpt3_fb = "gpt-3.5-turbo-0613"
    gpt3_16k = "gpt-3.5-turbo-16k"


class ArtPiece(Enum):
    mona_lisa = "Mona Lisa"

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
    gpt3 = "gpt-3.5-turbo-0125"
    gpt3_fb = "gpt-3.5-turbo-0613"
    gpt3_16k = "gpt-3.5-turbo-16k"



class ArtPiece(Enum):
    mona_lisa = "Mona Lisa"
    the_starry_night = "The Starry Night"
    girl_with_a_pearl_earring = "Girl with a Pearl Earring"
    the_kiss = "The Kiss"
    the_birth_of_venus = "The Birth of Venus"
    guernica = "Guernica"


class Postures(Enum):
    stand = "stand"
    sit = "sit"
    lay = "lay"

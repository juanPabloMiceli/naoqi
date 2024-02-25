from workspace.external_modules.chat.nao_chat.enums import OpenAIModel


ROOT = "/app/workspace/external_modules/chat/nao_chat"
PROMPT_STORE_PATH = f"{ROOT}/chatbots/prompts"
MAX_TOKENS_PER_REQUEST = 100000
TEMPERATURE = 0

OPENAI_MODEL = OpenAIModel.gpt3
SHOW_INSTRUCTIONS = True

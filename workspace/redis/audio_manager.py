from typing import Optional

import redis


class RedisAudioManager:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_conn = redis.Redis(host=host, port=port, db=db)

    def _add_prefix(self, key: str) -> str:
        return f"audio_module:{key}"

    def turn_on_hearing(self) -> None:
        self.redis_conn.set(self._add_prefix("hearing_status"), 1)

    def turn_off_hearing(self) -> None:
        self.redis_conn.set(self._add_prefix("hearing_status"), 0)

    def check_hearing_permission(self) -> bool:
        return self.redis_conn.get(self._add_prefix("hearing_status")) == b"1"

    def store_usage_message(self, message: str) -> None:
        self.redis_conn.set(self._add_prefix("user_message"), message)

    def consume_user_message(self) -> Optional[str]:
        user_message = self.redis_conn.get(self._add_prefix("user_message"))
        if user_message:
            user_message = user_message.decode("utf-8")
            self.redis_conn.delete(self._add_prefix("user_message"))
        return user_message

    def user_message_available(self) -> bool:
        return self.redis_conn.exists(self._add_prefix("user_message"))

    def store_chat_response(self, response: str) -> None:
        self.redis_conn.set(self._add_prefix("chat_response"), response)

    def consume_chat_response(self) -> Optional[str]:
        chat_response = self.redis_conn.get(self._add_prefix("chat_response"))
        if chat_response:
            chat_response = chat_response.decode("utf-8")
            self.redis_conn.delete(self._add_prefix("chat_response"))
        return chat_response

    def chat_response_available(self) -> bool:
        return self.redis_conn.exists(self._add_prefix("chat_response"))

    def store_user_intent(self, intent: str) -> None:
        self.redis_conn.set(self._add_prefix("user_intent"), intent)

    def consume_user_intent(self) -> Optional[str]:
        user_intent = self.redis_conn.get(self._add_prefix("user_intent"))
        if user_intent:
            user_intent = user_intent.decode("utf-8")
            self.redis_conn.delete(self._add_prefix("user_intent"))
        return user_intent

    def user_intent_available(self) -> bool:
        return self.redis_conn.exists(self._add_prefix("user_intent"))

    def clear_redis_keys(self) -> None:
        keys_to_clear = [
            self._add_prefix(key)
            for key in [
                "hearing_status",
                "user_message",
                "chat_response",
                "user_intent",
            ]
        ]
        self.redis_conn.delete(*keys_to_clear)

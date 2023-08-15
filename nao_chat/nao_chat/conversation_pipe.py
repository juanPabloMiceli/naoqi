from typing import Union

import redis
from nao_chat.enums import ChatRoles


class ConversationPipe:
    """
    A conversation class to manage the shown conversation on gradio
    """

    def __init__(self) -> None:
        # start redis conn
        self.client = redis.Redis(host="nao_chat-redis", port=6379, db=0)

    def clear(self) -> None:
        # removes redis convo
        # Retrieve all keys with a common prefix using the SCAN command
        keys_to_delete = []
        for role in ChatRoles:
            for key in self.client.scan_iter(f"{role.value}:*"):
                keys_to_delete.append(key)

        # Delete the keys individually
        for key in keys_to_delete:
            self.client.delete(key)

    def _set_message_availability(self, role: ChatRoles, available: bool) -> None:
        # set the given role message avalability as given
        self.client.set(f"{role.value}:availability", int(available))

    def _get_message_availability(self, role: ChatRoles) -> bool:
        # get the given role message avalability as given
        availability = self.client.get(f"{role.value}:availability")

        # if it isnt available, then return false
        if availability is None:
            availability = 0
        else:
            # redis responses are in bytes
            availability = int(availability)

        return bool(availability)

    def get_user_message_availability(self) -> bool:
        return self._get_message_availability(ChatRoles.user)

    def get_bot_message_availability(self) -> bool:
        return self._get_message_availability(ChatRoles.assistant)

    def _add_message(self, role: ChatRoles, message: str) -> None:
        # add message to the redis convo
        self.client.set(f"{role.value}:messsage", message)

        # set the message as available forthe given role
        self._set_message_availability(role, True)

    def add_user_message(self, message: str) -> None:
        self._add_message(ChatRoles.user, message)

    def add_bot_message(self, message: str) -> None:
        self._add_message(ChatRoles.assistant, message)

    def _get_available_message(self, role: ChatRoles) -> Union[str, None]:
        # set the message as unavailable, as it will be consumed
        self._set_message_availability(role, False)

        # retrieve the message from redis
        bytes_message = self.client.get(f"{role.value}:messsage")
        return bytes_message.decode("utf-8")

    def get_user_message(self) -> Union[str, None]:
        return self._get_available_message(ChatRoles.user)

    def get_bot_message(self) -> Union[str, None]:
        return self._get_available_message(ChatRoles.assistant)

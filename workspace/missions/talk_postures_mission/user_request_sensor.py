"""User request sensing module (interacts with redis)
"""


class UserRequestSensing:
    def __init__(self, nao, redis):
        self.nao = nao
        self.redis = redis

    def sense(self):
        user_request = self.redis.get("user_request")

        if user_request is None:
            return
        else:
            self.redis.delete("user_request")
            self.nao.shared_memory.add_message(user_request)

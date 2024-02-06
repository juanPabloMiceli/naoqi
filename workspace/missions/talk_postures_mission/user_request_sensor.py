"""User request sensing module (interacts with redis)
"""


class UserRequestSensing:
    def __init__(self, nao, redis_manager):
        self.nao = nao
        self.redis_manager = redis_manager

    def sense(self):
        user_request = self.redis_manager.consume_user_request()

        if user_request is None:
            return
        else:
            self.nao.shared_memory.add_message(user_request)

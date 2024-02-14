import redis


class RedisManager:

    SWITCHES = ["hearing", "talk"]

    PIPES = ["user_message", "chat_response", "nao_message", "user_request"]

    def __init__(self, host="nao-redis", port=6379, db=0):
        self.redis_conn = redis.Redis(host=host, port=port, db=db)

        # initialize switches functions

        for switch_identifier in RedisManager.SWITCHES:
            setattr(
                self,
                self.turn_on_switch.__name__.replace("switch", switch_identifier),
                lambda: self.turn_on_switch(switch_identifier),
            )
            setattr(
                self,
                self.turn_off_switch.__name__.replace("switch", switch_identifier),
                lambda: self.turn_off_switch(switch_identifier),
            )
            setattr(
                self,
                self.switch_status.__name__.replace("switch", switch_identifier),
                lambda: self.switch_status(switch_identifier),
            )

        # initialize pipe functions

        for pipe_identifier in RedisManager.PIPES:
            setattr(
                self,
                self.store_pipe.__name__.replace("pipe", pipe_identifier),
                lambda x: self.store_pipe(pipe_identifier, x),
            )
            setattr(
                self,
                self.consume_pipe.__name__.replace("pipe", pipe_identifier),
                lambda: self.consume_pipe(pipe_identifier),
            )
            setattr(
                self,
                self.pipe_available.__name__.replace("pipe", pipe_identifier),
                lambda: self.pipe_available(pipe_identifier),
            )

    def _add_prefix(self, key):
        return f"nao_chat:{key}"

    def turn_on_switch(self, switch_identifier):
        self.redis_conn.set(self._add_prefix(switch_identifier), 1)

    def turn_off_switch(self, switch_identifier):
        self.redis_conn.set(self._add_prefix(switch_identifier), 1)

    def switch_status(self, switch_identifier):
        return self.redis_conn.get(self._add_prefix(switch_identifier)) == b"1"

    def store_pipe(self, pipe_identifier, message):
        self.redis_conn.set(self._add_prefix(pipe_identifier), message)

    def consume_pipe(self, pipe_identifier):
        user_message = self.redis_conn.get(self._add_prefix(pipe_identifier))
        if user_message:
            user_message = user_message.decode("utf-8")
            self.redis_conn.delete(self._add_prefix(pipe_identifier))
        return user_message

    def pipe_available(self, pipe_identifier):
        return self.redis_conn.exists(self._add_prefix(pipe_identifier))

    def clear_redis_keys(self):
        keys_to_clear = [
            self._add_prefix(key) for key in RedisManager.SWITCHES + RedisManager.PIPES
        ]
        self.redis_conn.delete(*keys_to_clear)

    # coding declarations
    # this declarionts will be rewritten when initializing.
    # these are here to help the coding proccess run smoothly with coding editors

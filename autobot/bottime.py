import time

class BotTimer:
    def __init__(self):
        self._monolithic = time.monolithic()
        self._unix_time = time.time()

    @property
    def unix_time(self):
        pass

    @property
    def time_spent(self):
        pass

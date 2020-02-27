import re
import random

import requests
import vk_requests


class Bot:
    def __init__(self):
        self._lp_ts = self._lp_key = self._lp_server = None

        self._API = vk_requests.create_api(service_token='aaeb61325aae0f0953f5530b10ae5542f5615b9e71c86748b9582ffa046a84acb8d4a90978cf677ae432c')

    def get_long_poll_server(self):
        lps = self._API.groups.getLongPollServer(group_id=180764984)
        self._lp_key, self._lp_server, self._lp_ts = lps['key'], lps['server'], lps['ts']

    def long_poll(self, wait=25):
        """
        Gets updates from VK Long Poll server
        :param wait: int: Seconds to wait before returning empty updates list
        :return: dict: {'ts': 00000000, 'updates': [list of updates]}
        """

        payload = {'act': 'a_check', 'key': self._lp_key, 'ts': self._lp_ts, 'wait': wait}
        request = requests.get(self._lp_server, params=payload, timeout=wait + 5)
        res = request.json()

        if 'failed' not in res:
            return res

        elif res['failed'] == 1:
            self._lp_ts = res['ts']
            return self.long_poll()
        elif res['failed'] in (2, 3):
            self.get_long_poll_server()
            return self.long_poll()
        else:
            raise Exception('VK returned lp response with unexpected "failed" value. Response: {}'.format(res))

    def get_updates(self, retries=0):
        try:
            response = self.long_poll()
            self._lp_ts = response['ts']
            return response['updates']

        except requests.exceptions.Timeout:
            if retries >= 3:
                raise
            return self.get_updates(retries + 1)

    def on_message(self, update):
        message = update['object']['message']
        if re.search(r'г+[ао]+р+о+х+', message['text'], flags=re.IGNORECASE):
            self._API.messages.send(peer_id=message['peer_id'], random_id=0, message='🤢' * random.randint(1, 5))
        elif re.search(r'🤢+', message['text'], flags=re.IGNORECASE):
            self._API.messages.send(peer_id=message['peer_id'], random_id=0, message=f'гар{"о" * random.randint(1, 4)}х')

    def run(self):
        self.get_long_poll_server()

        while True:
            # Get updates from VK Long Poll server
            updates = self.get_updates()

            for update in updates:
                if update['type'] == 'message_new':
                    self.on_message(update)


if __name__ == '__main__':
    b = Bot()
    b.run()


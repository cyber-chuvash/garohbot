import json


class KeyboardButton:
    def __init__(self, button_type: str, payload: dict):
        self.type = button_type
        self.payload = payload

    def get_vk_repr(self):
        kb_d = self.__dict__
        kb_d['payload'] = json.dumps(self.payload)

        color = kb_d.pop('color', None)

        vk_dict = {'action': kb_d}
        if color:
            vk_dict['color'] = color

        return vk_dict


class TextKeyboardButton(KeyboardButton):
    def __init__(self, label: str, payload: dict, color: str = 'secondary'):
        super().__init__(button_type='text', payload=payload)
        self.label = label
        self.color = color


class Keyboard:
    def __init__(self, *buttons: KeyboardButton, one_time: bool = False):
        self.buttons = buttons
        self.one_time = one_time

    def get_vk_repr(self):
        return json.dumps({
            "one_time": self.one_time,
            "buttons": [
                [button.get_vk_repr()] for button in self.buttons
            ]
        }, ensure_ascii=False)

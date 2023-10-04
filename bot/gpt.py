from config import OPENAI_API_KEY, OPENAI_ORG
import openai

openai.organization = OPENAI_ORG
openai.api_key = OPENAI_API_KEY

class ChatGPTException(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return f'{self.message}'

class ChatGPT:
    def __init__(self):
        self.chats = {}
        self._default_sys_prompt = '''
            You are in a conversation with 1 or more people.
            In the conversation you are known as "OGM-72 'DIABLO' Strike". Or "Diablo Strike" for short.
            Each participant's messages, exept yours, will be prepented with their username. 
            An example of a message could be: "John: Hello everyone!"
            Diablo Strike is the capitan of a spaceship so try to stay in this role.
        '''
    
    def start_chat(self, chat_id: str, system_prompt=None):
        _chat_id = str(chat_id)
        if self.chats.get(_chat_id, None) is not None:
            raise ChatGPTException('Chat already exists')
        if system_prompt is None:
            system_prompt = self._default_sys_prompt

        self.chats[_chat_id] = {}

        self._add_msg(_chat_id, system_prompt, role='system')
    
    def send_message(self, chat_id: str, message: str):
        _chat_id = str(chat_id)
        self._add_msg(_chat_id, message)
        return self._send_chat(_chat_id)

    
    def _send_chat(self, chat_id) -> dict:
        self._check_chat(chat_id)
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.chats[chat_id]['messages']
        )

    def _add_msg(self, chat_id, content, role='user'):
        self._check_chat(chat_id)
        message = {
            'role': role,
            'content': content
        }
        chat = self.chats[chat_id]
        if not chat.get("messages", None):
            chat['messages'] = [message]
        else:
            chat['messages'].append(message)

    def _check_chat(self, chat_id):
        if self.chats.get(chat_id, None) is None:
            raise ChatGPTException('Chat does not exist')
import json

from util.route import route
from util.log import logger

import openai
import tornado.web
import os
import requests
import traceback

openai.api_key = os.environ.get("API_KEY")
dd_token = os.environ.get("DD_TOKEN")

# Set up the model and prompt
model_engine = "gpt-3.5-turbo"

retry_times = 5

global_dict = {}


@route("/")
class ChatgptHandler(tornado.web.RequestHandler):

    def get(self):
        return self.write_json({"ret": 200})

    def post(self):
        try:
            request_data = self.request.body
            data = json.loads(request_data)
            prompt = data['text']['content']
            if (prompt == '/clear'):
                self.clearContext(data)
                self.notify_dingding('已清空上下文')
                return self.write_json({"ret": 200})

            for i in range(retry_times):
                try:
                    context = self.getContext(data)
                    new_context = [
                        {"role": "user", "content": prompt}]
                    completion = openai.ChatCompletion.create(
                        model=model_engine,
                        messages=context + new_context,
                    )
                    response = completion.choices[0].message.content
                    usage = completion.usage
                    break
                except:
                    traceback.print_exc()
                    logger.info(f"failed, retry")
                    continue

            logger.info(f"parse response: {response}")
            self.setContext(data, response)
            self.notify_dingding(
                response + '\n' + '-=-=-=-=-=-=-=-=-=' + '\n' + '本次对话 Tokens 用量 [' + str(usage.total_tokens) + '/4096]')
            if (usage.total_tokens > 4096):
                self.clearContext(data)
                self.notify_dingding('超出 Tokens 限制，清空上下文')
            return self.write_json({"ret": 200})
        except:
            traceback.print_exc()
            return self.write_json({"ret": 500})

    def getContext(self, data):
        storeKey = self.getContextKey(data)
        if (global_dict.get(storeKey) is None):
            global_dict[storeKey] = []
        return global_dict[storeKey]

    def getContextKey(self, data):
        conversation_id = data['conversationId']
        sender_id = data['senderId']
        return conversation_id + '@' + sender_id

    def setContext(self, data, response):
        prompt = data['text']['content']
        storeKey = self.getContextKey(data)
        if (global_dict.get(storeKey) is None):
            global_dict[storeKey] = []
        global_dict[storeKey].append({"role": "user", "content": prompt})
        global_dict[storeKey].append(
            {"role": "assistant", "content": response})

    def clearContext(self, data):
        store_key = self.getContextKey(data)
        global_dict[store_key] = []

    def write_json(self, struct):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(tornado.escape.json_encode(struct))

    def notify_dingding(self, answer):
        data = {
            "msgtype": "text",
            "text": {
                "content": answer
            },

            "at": {
                "atMobiles": [
                    ""
                ],
                "isAtAll": False
            }
        }

        notify_url = f"https://oapi.dingtalk.com/robot/send?access_token={dd_token}"
        try:
            r = requests.post(notify_url, json=data)
            reply = r.json()
            logger.info("dingding: " + str(reply))
        except Exception as e:
            logger.error(e)

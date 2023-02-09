import json

from util.route import route
from util.log import logger

import openai
import tornado.web
import os
import requests

openai.api_key = os.environ.get("API_KEY")
dd_token = os.environ.get("DD_TOKEN")

# Set up the model and prompt
model_engine = "text-davinci-003"

retry_times = 5

@route("/")
class ChatgptHandler(tornado.web.RequestHandler):

    def get(self):
        return self.write_json({"ret": 200})

    def post(self):

        request_data = self.request.body;
        data = json.loads(request_data)
        prompt = data['text']['content']

        for i in range(retry_times):
            try:
                completion = openai.Completion.create(
                    engine=model_engine,
                    prompt=prompt,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
                response = completion.choices[0].text
                break
            except:
                logger.info(f"failed, retry")
                continue

        logger.info(f"parse response: {response}")
        self.notify_dingding(response)
        return self.write_json({"ret": 200})

    def write_json(self, struct):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(tornado.escape.json_encode(struct))

    def notify_dingding(self, answer):
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "chatgpt: ",
                "text": answer
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

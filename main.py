

import asyncio
import tornado
from util.route import route
import app


class Application(tornado.web.Application):
    def __init__(self):
        routed_handlers = route.get_routes()
        super(Application, self).__init__(routed_handlers)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    http_server = tornado.httpserver.HTTPServer(Application())
    print("Starting tornado on port [8080]", )
    http_server.listen(8080, "0.0.0.0")

    loop.run_forever()

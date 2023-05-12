from computational_captcha.controllers import captcha
from litestar import Router

routes = Router(path="/controller", route_handlers=[captcha.router])

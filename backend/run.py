import uvicorn
from computational_captcha.main import app


def main():
    uvicorn.run(app)

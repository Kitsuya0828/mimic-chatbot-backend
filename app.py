from flask import Flask, abort
from flask import request
from pathlib import Path
from urllib.request import urlopen
import os
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, AudioMessage, AudioSendMessage)
import librosa
import io
import soundfile as sf
import numpy as np
import tempfile
import audio_format
from time import sleep

# generate instance
app = Flask(__name__, static_url_path="/static")

# get environmental value from heroku
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# endpoint
@app.route("/")
def test():
    return "<h1>It Works!</h1>"

# endpoint from linebot
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle message from LINE
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
    
@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)
    
    # message = f"message_content {message_content.content}"
    # message = message[:min(len(message), 1000)]
    message = ""
    
    audio_path = Path(f"static/audio/{message_id}.m4a").absolute()
    try:
        # tfile = tempfile.NamedTemporaryFile(delete=False)
        # tfile.write(message_content.content)
        
        # message += f"file_name {tfile.name}\n"
        
        with open(audio_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        
        message += "write finished\n"
        original_content_url=f'https://mimic-chatbot-backend.herokuapp.com/static/audio/{message_id}.m4a'
        
        # line_bot_api.reply_message(
        # event.reply_token,
        # TextSendMessage(f"{audio_path}\n"))
        message += f"{audio_path}\n"
        # message += f"path {Path.cwd()}\n"
        # message += f"{os.listdir('static/audio')}\n"
        # # with urlopen(original_content_url) as response:
        # #     x, fs = sf.read(io.BytesIO(response.read()))
        # x, fs = sf.read(tfile.name)
        # message += "sf succeeded\n"
        file_path = Path(f"static/audio/{message_id}.m4a")
        message += f"1. {file_path.exists()}\n"
        
        file_path = Path(f"static/audio/{message_id}.m4a").absolute()
        message += f"2. {file_path.exists()}\n"
        
        file_path = f"static/audio/{message_id}.m4a"
        message += f"3. {file_path.exists()}\n"
        
        file_path = f"/app/static/audio/{message_id}.m4a"
        message += f"4. {file_path.exists()}\n"
        # try:
        #     x, fs = librosa.load(file_path)
        #     # # message += f"fs={fs}\n"
        #     message += "load finished\n"
        #     x = audio_format.byte_to_float(message_content.content)
        #     fs = 22050
        

        # # x = np.frombuffer(message_content.content)
        # # message += f"shape {x.shape}\n"
    
        #     feature = librosa.feature.spectral_centroid(x, fs)
        #     message += f"feature {feature}\n"
        #     message += ",".join([str(hoge) for hoge in feature[0]])
        # except Exception as e:
        #     message += f'error: {e}'
    except Exception as e:
        message += f"error: {e}"
    
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=f"Yeah!!{message[:1000]}"))        

if __name__ == "__main__":
	app.run()
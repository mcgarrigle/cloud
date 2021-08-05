from flask import Flask, request, Response
import uuid

app = Flask(__name__)

hooks = {}

@app.route("/<id>", methods=['GET'])
def webhook_get(id):
    return hooks[id]

@app.route("/", methods=['POST'])
def webhook_post():
    id = uuid.uuid4().hex
    hooks[id] = request.get_data(as_text=True)
    resp = Response()
    resp.status = '201'
    resp.headers['location'] = f"/{id}"
    return resp

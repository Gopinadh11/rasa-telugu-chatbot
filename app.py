import asyncio
import os
from rasa.core.agent import Agent
from flask import Flask, abort, request
from flask_cors import CORS, cross_origin
from rasa.core.utils import EndpointConfig
from rasa.core.tracker_store import MongoTrackerStore, TrackerStore, InMemoryTrackerStore, RedisTrackerStore
from rasa.core.domain import Domain, TemplateDomain
import logging
import rasa.core
from flask_cors import CORS, cross_origin
from flask import jsonify
import json


app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
logging.getLogger('flask_cors').level = logging.DEBUG

## loading Action endpoins
action_endpoint = "https://a2zbillactionserver.dealwallet.com/webhook"


def get_agents_dict():
    models_path = 'C:/Users/Gopi/Desktop/t-chatbot/models/'
    dirs = os.listdir(models_path)
    print("Dir entries::", dirs)
    agent_dict = {}
    temp = 1
    for sub_dir in dirs:
        agent_path = models_path + sub_dir
        agent_tar_path = os.listdir(agent_path)
        for model in agent_tar_path:
            model_path = agent_path + "/" + model
            print(model_path)
            agent = Agent.load(model_path, action_endpoint=EndpointConfig(action_endpoint))
            print(type(agent))
            print(agent)
            agent_dict["org" + str(temp)] = agent
            temp = temp + 1
    print("agent dic:", agent_dict)
    return agent_dict


async def process(agent, msg):
    output_data = await agent.handle_text(msg)
    print(output_data)
    return output_data


all_agents = get_agents_dict()


@app.route('/message', methods=['POST'])
@cross_origin(origin='*')
def get_chat_message():
    if not request.json:
        abort(400)

    try:
        org_value = request.args.get('orgId')

    except KeyError:
        raise ValueError("orgId query parameter not getting in request")

    current_agent = all_agents[org_value]
    try:
        user = request.json['sender']
    except KeyError:
        raise ValueError("sender field is not getting in request payload")
    try:
        message = request.json['message']
    except KeyError:
        raise ValueError("message field is not getting in request payload")
    print("message is:", message)
    print("user is:", user)
    print("orgid is:", org_value)

    result = asyncio.run(process(current_agent, message))
    result = json.dumps(result)
    return result


@app.route('/', methods=['GET'])
@cross_origin(origin='*')
def get_chat_response():
    return "Welcome to Flask Agents App"


if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True, use_reloader=False)


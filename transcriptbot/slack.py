import requests
import json

MIC_EMOJI_IMAGE = "http://i.imgur.com/mHbOS5y.png"


def slack_thread(hook_url, name, queue):
    try:
        post_to_slack(hook_url, name, "_starts recording_")
        while True:
            transcript = queue.get()
            post_to_slack(hook_url, name, transcript)
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass


def post_to_slack(hook_url, name, transcript):
    data = json.dumps(dict(
        username="%s's Mic" % name,
        text=transcript,
        icon_url=MIC_EMOJI_IMAGE,
        mrkdwn=True
    ))
    headers = {'Content-Type': "application/json"}
    requests.post(hook_url, data=data, headers=headers)

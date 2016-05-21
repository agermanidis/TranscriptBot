![img](http://i.imgur.com/mAaNgvr.gif)

## TranscriptBot: Real-time voice transcription Slack bot

### Introduction

TranscriptBot is a command-line utility that listens to the sound input from your mic, transcribes each sentence it hears using the Google Web Speech API, and posts it to Slack in real-time. It lets people on your team who are not physically present follow along a meeting or conversation without having to join in a video conference call.

### Installation

1. Install ffmpeg: `brew install ffmpeg` (Mac OS X) or `apt-get install ffmpeg` (Ubuntu).
2. Install portaudio: `brew install portaudio` (Mac OS X) or `apt-get install portaudio19-dev` (Ubuntu).
2. Install TranscriptBot: `pip install transcriptbot`

### Setting up an incoming webhook for your channel

To use TranscriptBot on a given Slack channel, you first need to set up an incoming webhook. Here's how:

1. Sign in to your Slack team and [create a new webhook](https://my.slack.com/services/new/incoming-webhook/) after selecting the channel you want your bot to post to.
2. Copy the resulting Webhook URL and add it to TranscriptBot:

```bash
$ transcriptbot hooks add my-new-hook https://hooks.slack.com/services/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

# if you want to use the hook in your next recording
$ transcriptbot hooks use my-new-hook
```

Repeat this process every time you want to post to a new channel.

### Usage options

```
transcriptbot - Real-time voice transcription Slack bot

Usage:
  transcriptbot record [-i <audio-device>] [--no-slack] [-k <hook-url>] [-n <name>]
  transcriptbot hooks add <hook-name> <hook-url>
  transcriptbot hooks remove <hook-name>
  transcriptbot hooks use <hook-name>
  transcriptbot hooks list
  transcriptbot list_audio_devices
  transcriptbot use_name <name>

Options:
  --version                        Show version.
  -h, --help                       Show this screen.
  -i, --audio-device               Specify audio device to record with (default = 0).
  -k, --hook-url                   Hook URL to use to post transcription to Slack.
  -n, --name                       Name to appear on Slack (default = your OS user name).
  --no-slack                       Print the transcripts but do not post them to Slack.
```

### License

MIT

import openai
import os
from google.cloud import texttospeech
import subprocess

def generate_chat(text, openai_api_key, chat_model="gpt-4"):
    """
    Generate a conversation between two hosts using ChatGPT.
    """
    openai.api_key = openai_api_key

    response = openai.ChatCompletion.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "You are Host 1, a curious podcast host."},
            {"role": "system", "content": "You are Host 2, a knowledgeable podcast co-host."},
            {"role": "user", "content": text},
        ],
        max_tokens=500,
    )

    return response['choices'][0]['message']['content']

def split_hosts(conversation):
    """
    Split the conversation into separate lines for Host 1 and Host 2.
    """
    host1_lines = []
    host2_lines = []

    for line in conversation.split("\n"):
        if line.startswith("Host 1:"):
            host1_lines.append(line.replace("Host 1:", "").strip())
        elif line.startswith("Host 2:"):
            host2_lines.append(line.replace("Host 2:", "").strip())

    return host1_lines, host2_lines

def synthesize_text(text, voice_name, output_file):
    """
    Use Google TTS to convert text to audio.
    """
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name=voice_name
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)

def merge_audio(host1_file, host2_file, output_file):
    """
    Merge two audio files alternately using ffmpeg.
    """
    command = [
        "ffmpeg",
        "-i", host1_file,
        "-i", host2_file,
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=longest",
        output_file
    ]

    subprocess.run(command, check=True)

def main():
    # Configuration
    openai_api_key = "your_openai_api_key_here"
    google_api_key_path = "path_to_google_api_key.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_api_key_path

    user_input = "Today we're discussing the impact of AI on creativity."

    # Generate conversation
    conversation = generate_chat(user_input, openai_api_key)
    host1_lines, host2_lines = split_hosts(conversation)

    # Synthesize audio for each host
    host1_text = " ".join(host1_lines)
    host2_text = " ".join(host2_lines)

    synthesize_text(host1_text, "en-US-Wavenet-D", "host1.mp3")
    synthesize_text(host2_text, "en-US-Wavenet-E", "host2.mp3")

    # Merge audio files
    merge_audio("host1.mp3", "host2.mp3", "podcast_final.mp3")

    print("Podcast generated: podcast_final.mp3")

if __name__ == "__main__":
    main()

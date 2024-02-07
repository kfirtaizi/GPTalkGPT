import os

import pygame as pygame
from openai import OpenAI

from recorder import Recorder

client = OpenAI()


def transcribe_audio(file_path):
    """Transcribe audio file to text using OpenAI's Whisper model."""
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    os.remove(file_path)
    return transcript.text


def text_to_speech(text):
    """Convert text to speech using OpenAI's TTS model."""
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    return response


def play_mp3(audio_file_path):
    pygame.mixer.init()

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue

        pygame.mixer.quit()
        os.remove(audio_file_path)

    except pygame.error as e:
        print(f"Error playing the audio: {str(e)}")


def chatgpt_response(text, model="gpt-3.5-turbo"):
    """
    Get a response from ChatGPT based on the input text.
    """
    messages = [{"role": "system",
                 "content": "Speak freely, keep your questions/answers short (sentence or two)"},
                {"role": "user", "content": text}]
    gpt_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return gpt_response.choices[0].message.content


recorder = Recorder()
while True:
    # Record audio
    audio_data = recorder.listen()
    recorder.save_audio_as_wav(audio_data, "input.wav")

    # Transcribe audio to text
    transcribed_text = transcribe_audio("input.wav")
    print("Transcribed Text:", transcribed_text)

    # Get response from ChatGPT
    response_text = chatgpt_response(transcribed_text)
    print("ChatGPT Response:", response_text)

    # Convert response to speech
    response_audio = text_to_speech(response_text)
    response_audio.stream_to_file("output.mp3")

    # Play the response
    play_mp3("output.mp3")

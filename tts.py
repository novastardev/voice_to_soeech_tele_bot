import time
import requests

from config import TTS_API_KEY

BASE_URL = "https://api.tts.ai/v1"

HEADERS = {
    "Authorization": f"Bearer {TTS_API_KEY}",
    "Content-Type": "application/json",
}


def get_voices():
    response = requests.get(
        f"{BASE_URL}/voices/",
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()
    return data.get("voices", [])


def generate_speech(text, voice):
    response = requests.post(
        f"{BASE_URL}/tts/",
        headers=HEADERS,
        json={
            "model": "kokoro",
            "text": text,
            "voice": voice,
            "format": "mp3"
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()
    job_uuid = data.get("uuid")

    if not job_uuid:
        raise RuntimeError("No TTS job ID was returned.")

    for _ in range(60):
        result = requests.get(
            f"{BASE_URL}/speech/results/",
            params={"uuid": job_uuid},
            headers=HEADERS,
            timeout=30
        )

        result.raise_for_status()
        result_data = result.json()

        status = result_data.get("status")

        if status == "completed":
            audio_url = result_data.get("result_url")

            if not audio_url:
                raise RuntimeError("No audio URL was returned.")

            audio = requests.get(audio_url, timeout=60)
            audio.raise_for_status()

            return audio.content

        if status == "failed":
            raise RuntimeError(
                result_data.get("error", "TTS generation failed.")
            )

        time.sleep(1.5)

    raise TimeoutError("TTS generation timed out.")
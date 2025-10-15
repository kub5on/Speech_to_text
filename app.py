import streamlit as st
import ffmpeg
import openai
from pathlib import Path
import os

st.set_option('server.maxUploadSize', 4096)  # 4 GB

# Ustaw klucz OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

col1, col2 = st.columns([1, 3])  # proporcje szerokości
with col1:
    st.image("logo.png", width=150)
with col2:
    st.title("Transkrypcja superwizji")

uploaded_file = st.file_uploader("Wybierz plik MOV", type=["mov"])
duration_per_chunk = 300  # sekundy

if uploaded_file is not None:
    # Zapisz plik tymczasowo
    input_file = Path("temp_input.mov")
    with open(input_file, "wb") as f:
        f.write(uploaded_file.read())

    # Wyczyszczenie pliku transkrypcji
    transcript_file = Path("transkrypcja.txt")
    transcript_file.write_text("", encoding="utf-8")

    # Pobranie długości wideo
    probe = ffmpeg.probe(str(input_file))
    total_duration = float(probe['format']['duration'])
    num_chunks = int(total_duration // duration_per_chunk) + 1

    full_text = ""
    progress_bar = st.progress(0)  # inicjalizacja paska postępu

    for i in range(num_chunks):
        start_time = i * duration_per_chunk
        mp3_file = Path(f"chunk_{i}.mp3")

        # Konwersja fragmentu do pliku głosowego
        # ffmpeg.input(str(input_file), ss=start_time, t=duration_per_chunk).output(str(wav_file)).run(overwrite_output=True)
        ffmpeg.input("temp_input.mov", ss=start_time, t=duration_per_chunk).output(f"chunk_{i}.mp3", ar=16000, ac=1, audio_bitrate="32k").run(overwrite_output=True)

        # Wysyłka do Whisper
        with open(mp3_file, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        text = f"Fragment {i}:\n{transcript.text}\n\n"
        full_text += text

        # Dopisanie do pliku
        with open(transcript_file, "a", encoding="utf-8") as f:
            f.write(text)

        # Usunięcie pliku WAV po transkrypcji
        os.remove(mp3_file)

        # Aktualizacja paska postępu
        progress_bar.progress((i + 1) / num_chunks)

    st.subheader("Transkrypcja:")
    st.text(full_text)
    st.success("Transkrypcja zakończona!")

    # Dodanie przycisku do pobrania transkrypcji
    st.download_button(
        label="Pobierz transkrypcję",
        data=transcript_file.read_text(encoding="utf-8"),
        file_name="transkrypcja.txt",
        mime="text/plain"
    )

    # Usunięcie pliku wejściowego po zakończeniu transkrypcji
    os.remove(input_file)
    os.remove(uploaded_file)

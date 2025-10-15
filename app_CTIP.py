import streamlit as st
from moviepy.editor import VideoFileClip
import openai
from pathlib import Path
import os

# Ustaw klucz OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Layout Streamlit
col1, col2 = st.columns([1, 3])
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

    # Wyczyszczenie pliku transkrypcji w pamięci
    full_text = ""

    # Wczytanie wideo
    clip = VideoFileClip(str(input_file))

    # Sprawdzenie, czy wideo ma audio
    if clip.audio is None:
        st.error("Wideo nie zawiera ścieżki audio!")
    else:
        st.success(f"Wideo zawiera audio o długości {clip.audio.duration:.2f} s")

        total_duration = clip.duration
        num_chunks = int(total_duration // duration_per_chunk) + 1

        progress_bar = st.progress(0)

        for i in range(num_chunks):
            start_time = i * duration_per_chunk
            end_time = min((i + 1) * duration_per_chunk, total_duration)
            mp3_file = Path(f"chunk_{i}.mp3")

            try:
                # Wyciągnięcie fragmentu audio
                audio_clip = clip.subclip(start_time, end_time).audio

                if audio_clip is None:
                    st.warning(f"Fragment {i} nie zawiera audio, pomijam.")
                    continue

                # Zapis MP3 (mono, 16kHz)
                audio_clip.write_audiofile(
                    str(mp3_file),
                    fps=16000,
                    nbytes=2,
                    codec="mp3",
                    ffmpeg_params=["-ac", "1"]  # mono
                )
                audio_clip.close()

                # Wysyłka do Whisper
                with open(mp3_file, "rb") as audio_file:
                    transcript = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )

                full_text += f"Fragment {i}:\n{transcript.text}\n\n"

            except Exception as e:
                st.error(f"Błąd podczas przetwarzania fragmentu {i}: {e}")

            finally:
                # Usuń plik mp3 po transkrypcji
                if mp3_file.exists():
                    os.remove(mp3_file)

            # Aktualizacja paska postępu
            progress_bar.progress((i + 1) / num_chunks)

        # Wyświetlenie transkrypcji
        st.subheader("Transkrypcja:")
        st.text(full_text)
        st.success("Transkrypcja zakończona!")

        # Dodanie przycisku do pobrania transkrypcji
        transcript_file = Path("transkrypcja.txt")
        transcript_file.write_text(full_text, encoding="utf-8")
        st.download_button(
            label="Pobierz transkrypcję",
            data=transcript_file.read_text(encoding="utf-8"),
            file_name="transkrypcja.txt",
            mime="text/plain"
        )

        # Sprzątanie plików tymczasowych
        if input_file.exists():
            os.remove(input_file)
        if transcript_file.exists():
            os.remove(transcript_file)
        clip.close()

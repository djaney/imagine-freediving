from pydub import AudioSegment
from gtts import gTTS
import os


def generate_audio_annotations(tmp_dir, output_path, annotations):
    audio_segments = {}
    for text, _ in annotations:
        file_path = f"{tmp_dir}/seg.{text}.mp3"
        if not os.path.isfile(file_path):
            gtts = gTTS(text=text, lang='en', slow=False)
            gtts.save(file_path)
        audio_segments[text] = AudioSegment.from_file(file_path, "mp3")

    main_audio = AudioSegment.empty()

    current_time = 0.0
    for text, xy in annotations:
        if type(xy) == tuple:
            x = xy[0]
        else:
            x = xy
        if current_time > x:
            raise Exception(f"{text} too close")
        silent_time = x - current_time
        if silent_time > 0:
            main_audio += AudioSegment.silent(silent_time * 1000)
        main_audio += audio_segments[text]
        current_time = main_audio.duration_seconds

    main_audio.export(f"{output_path}", format="mp3")
    return main_audio.duration_seconds

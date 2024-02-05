from freediving import Dive
from gtts import gTTS
from pydub import AudioSegment
import os
import tempfile
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Generate audio file for a guided visualization of a freedive',
        epilog='Text at the bottom of help')

    parser.add_argument('filename', help="file name with .mp3")
    parser.add_argument('target_depth', type=int, help="Target depth in meters")
    parser.add_argument('descent_rate', type=float, help="Descent rate in positive meters per second")
    parser.add_argument('ascent_rate', type=float, help="Ascent rate in positive meters per second")
    parser.add_argument('--charge', type=float, help="Depth to charge mouthfill")
    parser.add_argument('--freefall', type=float, help="Depth to freefall")
    parser.add_argument('--float', type=float, help="Depth to let neutral buoyancy take over")
    args = parser.parse_args()

    assert args.filename[-4:] == ".mp3", "file should be mp3"

    dive = Dive.generate(args.target_depth, args.descent_rate, args.ascent_rate)
    dive.annotate_by_meters(0, "dive")
    if args.charge:
        dive.annotate_by_meters(args.charge, "charge")
    if args.freefall:
        dive.annotate_by_meters(args.freefall, "freefall")
    if args.float:
        dive.annotate_by_meters(args.float, "float", ascend=True)
    dive.annotate_by_meters(0, "breathe", ascend=True)
    dive.peak_to_annotation("grab tag and turn")
    x_points, y_points, annotations = dive.get_plot_data()

    with tempfile.TemporaryDirectory() as tmp_dir:

        # create sound files
        audio_segments = {}
        for text, (x, y) in annotations:
            file_path = f"{tmp_dir}/{text}.mp3"
            if not os.path.isfile(file_path):
                gtts = gTTS(text=text, lang='en', slow=False)
                gtts.save(file_path)
            audio_segments[text] = AudioSegment.from_file(file_path, "mp3")

        main_audio = AudioSegment.empty()

        current_time = 0.0
        for text, (x, y) in annotations:
            if current_time > x:
                raise Exception(f"{text} too close")
            silent_time = x-current_time
            if silent_time > 0:
                main_audio += AudioSegment.silent(silent_time * 1000)
            main_audio += audio_segments[text]
            current_time = main_audio.duration_seconds

        main_audio.export(f"{args.filename}", format="mp3")


if __name__ == "__main__":
    main()

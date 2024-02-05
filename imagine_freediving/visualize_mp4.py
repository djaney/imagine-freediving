from freediving import Dive
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import os
import tempfile
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def main():
    parser = argparse.ArgumentParser(
        description='Generate video file for a guided visualization of a freedive')

    parser.add_argument('filename', help="file name with .mp4")
    parser.add_argument('target_depth', type=int, help="Target depth in meters")
    parser.add_argument('descent_rate', type=float, help="Descent rate in positive meters per second")
    parser.add_argument('ascent_rate', type=float, help="Ascent rate in positive meters per second")
    parser.add_argument('--charge', type=float, help="Depth to charge mouthfill")
    parser.add_argument('--freefall', type=float, help="Depth to freefall")
    parser.add_argument('--float', type=float, help="Depth to let neutral buoyancy take over")
    args = parser.parse_args()

    assert args.filename[-4:] == ".mp4", "file should be mp4"

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

        video_path = f"{tmp_dir}/video.mp4"
        audio_path = f"{tmp_dir}/audio.mp3"

        # generate video
        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.fill_between(x_points, y_points, alpha=1)
        ax.fill_between(x_points[:0], y_points[:0], alpha=0.7)

        for a in annotations:
            ax.annotate(*a)

        def animate(i):
            ax.clear()
            ax.fill_between(x_points, y_points, alpha=1)
            ax.fill_between(x_points[:i], y_points[:i], alpha=0.7)
            for a in annotations:
                ax.annotate(*a)

        ani = animation.FuncAnimation(fig, animate, frames=len(x_points), interval=1000)
        ani.save(video_path)

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

        main_audio.export(audio_path, format="mp3")

        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)
        video.write_videofile(args.filename)


if __name__ == "__main__":
    main()

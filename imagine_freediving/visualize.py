from freediving import Dive
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips
from imagine_freediving.audio import generate_audio_annotations
from imagine_freediving.video import generate_dive_video, generate_rest_video
import tempfile
import argparse

THEME = {
    "bg": [0, 71, 201],
    "overlay": [225, 225, 225],
}

def main():
    parser = argparse.ArgumentParser(
        description='Generate video/audio file for a guided visualization of a freedive')

    parser.add_argument('filename', help="file name with .mp4/.mp3")
    parser.add_argument('--generate', nargs=3, type=float, help="{target depth} {descent rate} {ascent rate}")
    parser.add_argument('--size', nargs=2, default=[1024, 768], type=int, help="Video size")
    parser.add_argument('--charge', type=float, help="Depth to charge mouthfill")
    parser.add_argument('--freefall', type=float, help="Depth to freefall")
    parser.add_argument('--float', type=float, help="Depth to let neutral buoyancy take over")
    parser.add_argument('--fps', type=int, default=24, help="frames per second")
    parser.add_argument('--reps', type=int, default=1, help="Workout reps")
    parser.add_argument('--rest', type=int, help="Seconds of rest")
    args = parser.parse_args()

    if args.filename[-4:] == ".mp4":
        video = True
    elif args.filename[-4:] == ".mp3":
        video = False
    else:
        raise Exception("invalid filename")

    if args.rest is not None and args.rest < 15:
        raise Exception("rest cannot be less than 10 seconds")

    # Generate dive
    if args.generate:
        t, d, a = args.generate
        dive = Dive.generate(int(t), d, a)
    else:
        raise Exception("No action")

    dive.annotate_by_meters(0, "dive")
    if args.charge:
        dive.annotate_by_meters(args.charge, "charge")
    if args.freefall:
        dive.annotate_by_meters(args.freefall, "freefall")
    if args.float:
        dive.annotate_by_meters(args.float, "float", ascend=True)
    dive.annotate_by_meters(0, "breathe", ascend=True)
    dive.peak_to_annotation("touch down")
    x_points, y_points, annotations = dive.get_plot_data()

    rest_annotations = [
        ("relax", 0),
        ("10 seconds", args.rest-10),
        ("5 seconds", args.rest-5),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        dive_audio_path = f"{tmp_dir}/dive.audio.mp3"
        rest_audio_path = f"{tmp_dir}/rest.audio.mp3"
        if video:
            # This green color should not be visible if video is properly filled at the end
            # create sound files
            audio_duration = generate_audio_annotations(tmp_dir, dive_audio_path, annotations)
            dive_audio = AudioFileClip(dive_audio_path)
            if args.rest is not None:
                rest_annotations = [
                    ("relax", 0),
                    ("10 seconds", args.rest - 10),
                    ("5 seconds", args.rest - 5),
                ]
                generate_audio_annotations(tmp_dir, rest_audio_path, rest_annotations)
                rest_audio = AudioFileClip(rest_audio_path)
                rest_video = generate_rest_video(args.size, args.rest, rest_annotations, THEME)
                rest_video = rest_video.set_audio(rest_audio)
            # build dive video
            dive_video = generate_dive_video(args.size, x_points, y_points, annotations, THEME, args.fps)
            # freeze if audio is longer
            extra_duration = audio_duration - dive_video.duration
            if extra_duration > 0:
                frozen = dive_video.rep_video(dive_video.duration).set_duration(extra_duration)
                dive_video = CompositeVideoClip([dive_video, frozen])

            dive_video = dive_video.set_audio(dive_audio)
            # generate video
            video_segments = []
            for i in range(args.reps):
                # rest video
                if args.rest is not None:
                    video_segments.append(rest_video)

                video_segments.append(dive_video)
            main_video = concatenate_videoclips(video_segments)
            main_video.write_videofile(args.filename, fps=args.fps)
        else:
            # create sound files
            generate_audio_annotations(tmp_dir, args.filename, annotations)


if __name__ == "__main__":
    main()

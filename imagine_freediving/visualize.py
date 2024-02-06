from freediving import Dive
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip
from imagine_freediving.audio import generate_audio
from imagine_freediving.video import generate_video
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
    args = parser.parse_args()

    if args.filename[-4:] == ".mp4":
        video = True
    elif args.filename[-4:] == ".mp3":
        video = False
    else:
        raise Exception("invalid filename")

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
    dive.peak_to_annotation("grab tag and turn")
    x_points, y_points, annotations = dive.get_plot_data()

    with tempfile.TemporaryDirectory() as tmp_dir:
        video_path = f"{tmp_dir}/video.mp4"
        audio_path = f"{tmp_dir}/audio.mp3"
        if video:
            # This green color should not be visible if video is properly filled at the end
            background_color = [100, 255, 100]
            # create sound files
            audio_duration = generate_audio(tmp_dir, audio_path, annotations)

            # generate video
            generated_video_clip = generate_video(args.size, x_points, y_points, annotations, THEME, args.fps)

            video = CompositeVideoClip([
                # Background clip with correct duration
                ColorClip(args.size, duration=audio_duration, color=background_color),
                generated_video_clip,
            ])
            audio = AudioFileClip(audio_path)
            video = video.set_audio(audio)
            video.write_videofile(args.filename, fps=args.fps)
        else:
            # create sound files
            generate_audio(tmp_dir, args.filename, annotations)


if __name__ == "__main__":
    main()

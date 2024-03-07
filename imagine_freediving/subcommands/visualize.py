from freediving import Dive, fit_to_session
from moviepy.editor import AudioFileClip, CompositeVideoClip, concatenate_videoclips
from imagine_freediving.audio import generate_audio_annotations
from imagine_freediving.video import generate_dive_video, generate_rest_video
import tempfile
import click

THEME = {
    "bg": [0, 71, 201],
    "overlay": [225, 225, 225],
}


@click.command()
@click.argument("filename", type=click.Path())
@click.option("--fit", type=click.Path(), help="Fit file")
@click.option("--fit_dive_number", type=int, help="Index of the dive within the fit file. First is 0")
@click.option("--target_depth", type=int)
@click.option('--descent', type=float, default=1.0, help="descent rate in m/s")
@click.option('--ascent', type=float, default=1.0, help="descent rate in m/s")
@click.option('--size', nargs=2, default=[1024, 768], type=int, help="Video size")
@click.option('--charge', type=float, help="Depth to charge mouthfill")
@click.option('--freefall', type=float, help="Depth to freefall")
@click.option('--float', type=float, help="Depth to let neutral buoyancy take over")
@click.option('--fps', type=int, default=24, help="frames per second")
@click.option('--reps', type=int, default=1, help="Workout reps")
@click.option('--rest', type=int, help="Seconds of rest")
def visualize(**args):
    """
    Generate video/audio file for a guided visualization of a freedive
    """

    if args['filename'][-4:] != ".mp4":
        raise click.BadArgumentUsage("only mp4 is allowed")

    if args['rest'] is not None and args['rest'] < 15:
        raise click.BadOptionUsage("rest", "rest cannot be less than 10 seconds")

    # Generate dive
    if args['target_depth']:
        dive = Dive.generate(args['target_depth'], args['descent'], args['ascent'])
    elif args['fit']:
        if not args['fit_dive_number']:
            raise click.BadOptionUsage("fit_dive_number", "--fit_dive_number must be defined")
        session = fit_to_session(args['fit'])
        dive = session.get_dive(args['fit_dive_number'])
    else:
        raise click.UsageError("--target_depth or --fit must be defined")

    dive.annotate_by_meters(0, "dive")

    if args['charge']:
        dive.annotate_by_meters(args['charge'], "charge")
    if args['freefall']:
        dive.annotate_by_meters(args['freefall'], "freefall")
    if args['float']:
        dive.annotate_by_meters(args['float'], "float", ascend=True)
    dive.annotate_by_meters(1, "breathe", ascend=True)
    dive.peak_to_annotation("touch down")
    x_points, y_points, annotations = dive.get_plot_data()

    with tempfile.TemporaryDirectory() as tmp_dir:
        dive_audio_path = f"{tmp_dir}/dive.audio.mp3"
        rest_audio_path = f"{tmp_dir}/rest.audio.mp3"
        # This green color should not be visible if video is properly filled at the end
        # create sound files
        audio_duration = generate_audio_annotations(tmp_dir, dive_audio_path, annotations)
        dive_audio = AudioFileClip(dive_audio_path)
        if args['rest'] is not None:
            rest_annotations = [
                ("relax", 0),
                ("10 seconds", args['rest'] - 10),
                ("5 seconds", args['rest'] - 5),
            ]
            generate_audio_annotations(tmp_dir, rest_audio_path, rest_annotations)
            rest_audio = AudioFileClip(rest_audio_path)
            rest_video = generate_rest_video(args['size'], args['rest'], rest_annotations, THEME)
            rest_video = rest_video.set_audio(rest_audio)
        # build dive video
        dive_video = generate_dive_video(args['size'], x_points, y_points, annotations, THEME, args['fps'])
        # freeze if audio is longer
        extra_duration = audio_duration - dive_video.duration
        if extra_duration > 0:
            frozen = dive_video.rep_video(dive_video.duration).set_duration(extra_duration)
            dive_video = CompositeVideoClip([dive_video, frozen])

        dive_video = dive_video.set_audio(dive_audio)
        # generate video
        video_segments = []
        for i in range(args['reps']):
            # rest video
            if args['rest'] is not None:
                video_segments.append(rest_video)

            video_segments.append(dive_video)
        main_video = concatenate_videoclips(video_segments)
        main_video.write_videofile(args['filename'], fps=args['fps'])

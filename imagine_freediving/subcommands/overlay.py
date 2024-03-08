from freediving import fit_to_session
from moviepy.editor import VideoFileClip, CompositeVideoClip
from PIL import Image
from imagine_freediving.overlays.dive_telemetry import DefaultDiveTelemetryOverlay
import tempfile
import click


@click.command()
@click.argument("input_path", type=click.Path())
@click.argument("fit", type=click.Path())
@click.argument("fit_dive_number", type=int)
@click.argument("video_output", type=click.Path())
@click.option("--dive_start_seconds", type=int, default=0)
@click.option("--preview", type=click.Choice(['none', 'touchdown', 'start', 'end']), default='none')
def overlay(**args):
    """
    Generate overlay
    """
    session = fit_to_session(args['fit'])
    dive = session.get_dive(args['fit_dive_number'])

    video_clip = VideoFileClip(args['input_path'])

    theme = {
        "bg": [0, 71, 201],
        "overlay": [225, 225, 225],
    }

    w, h = size = video_clip.size


    x_points, y_points, annotations = dive.get_plot_data()

    overlay_width = int(min(w, h) // 3)
    overlay_height = overlay_width // 2
    pad = overlay_width // 10
    overlay_clip = DefaultDiveTelemetryOverlay(x_points, y_points, (overlay_width, overlay_height), theme,
                                               video_clip.fps).make_clip()
    # adjust position based on size
    overlay_clip = overlay_clip.set_position((w - pad - overlay_width, h - overlay_height - pad))

    main_clip = CompositeVideoClip([
        video_clip,
        overlay_clip.set_start(args['dive_start_seconds']),
    ], size=size)
    if args['preview'] != 'none':
        t = 0
        if args['preview'] == 'touchdown':
            t = args['dive_start_seconds'] + (x_points[-1]/2)
        elif args['preview'] == 'start':
            t = args['dive_start_seconds']
        elif args['preview'] == 'end':
            t = args['dive_start_seconds'] + (x_points[-1])
        np_image = main_clip.get_frame(t=t)
        im = Image.fromarray(np_image).convert('RGB')
        im.show()
    else:
        main_clip.write_videofile(
            args['video_output'], fps=video_clip.fps, temp_audiofile="temp-audio.m4a", remove_temp=True,
            codec="libx264", audio_codec="aac")

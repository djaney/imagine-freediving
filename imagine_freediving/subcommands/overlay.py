import datetime

from freediving import fit_to_session
from moviepy.editor import VideoFileClip, CompositeVideoClip
from PIL import Image
from imagine_freediving.overlays.dive_telemetry import DefaultDiveTelemetryOverlay
from imagine_freediving.overlays.label import Label
import click


@click.command()
@click.argument("input_path", type=click.Path())
@click.argument("fit", type=click.Path())
@click.argument("video_output", type=click.Path())
@click.option("--dive_index", type=int, default=None)
@click.option("--official_top", type=click.DateTime(), default=None)
@click.option("--official_top_start_seconds", type=int, default=0)
@click.option("--dive_start_seconds", type=int, default=0)
@click.option("--label", type=str, default=None)
@click.option("--preview", type=click.Choice(['none', 'touchdown', 'start', 'end']), default='none')
def overlay(**args):
    """
    Generate overlay
    Usage:
    overlay <input video> <garmin file> <video output> --dive_index <index> --dive_start_seconds <dive start in video>
    OR
    overlay <input video> <garmin file> <video output> --official_top <official top> --official_top_start_seconds <OT start in video>

    official top timezone is assumed to be computer's timezone
    """
    handle_overlay(**args)


def handle_overlay(**args):
    session = fit_to_session(args['fit'])
    official_top = None
    if args['dive_index']:
        dive = session.get_dive(args['dive_index'])
    elif args['official_top']:
        official_top = args['official_top'].replace(tzinfo=datetime.datetime.now().astimezone().tzinfo)
        dive = session.get_dive_by_time(official_top)
    else:
        raise click.BadOptionUsage("dive_index", "Provide either --dive_index or --official_top")

    video_clip = VideoFileClip(args['input_path'])

    theme = {
        "bg": [0, 71, 201],
        "overlay": [225, 225, 225],
        "font": "Arial"
    }

    w, h = size = video_clip.size

    ts_points, x_points, y_points, annotations = dive.get_plot_data(with_ts=True)

    overlay_width = int(min(w, h) // 3)
    overlay_height = overlay_width // 2
    pad = overlay_width // 10

    label_height = 0
    label_pad = 0
    label_font_size = 0

    if args['label']:
        label_font_size = 24
        label_height = label_font_size + pad
        label_pad = pad

    overlay_clip = DefaultDiveTelemetryOverlay(x_points, y_points, (overlay_width, overlay_height), theme,
                                               video_clip.fps).make_clip()
    # adjust position based on size
    overlay_clip = overlay_clip.set_position(
        (w - pad - overlay_width,
         h - overlay_height - pad - label_height - label_pad)
    )

    if args['dive_start_seconds']:
        offset = args['dive_start_seconds']
    else:
        ot_to_dive = ts_points[0] - official_top
        offset = args['official_top_start_seconds'] + ot_to_dive.total_seconds()
    overlay_clip = overlay_clip.set_start(offset)

    clip_list = [
        video_clip,
        overlay_clip,
    ]

    if args['label']:
        label_clip = Label(
            (0, h - pad - label_height),
            (w, label_height),
            args['label'],
            label_font_size, theme).make_clip()
        label_clip = label_clip.set_start(0).set_duration(video_clip.duration)
        clip_list.append(label_clip)

    main_clip = CompositeVideoClip(clip_list, size=size)

    if args['preview'] != 'none':
        t = 0
        if args['preview'] == 'touchdown':
            t = offset + (x_points[-1] / 2)
        elif args['preview'] == 'start':
            t = offset
        elif args['preview'] == 'end':
            t = offset + (x_points[-1])
        np_image = main_clip.get_frame(t=t)
        im = Image.fromarray(np_image).convert('RGB')
        im.show()
    else:
        main_clip.write_videofile(
            args['video_output'], fps=video_clip.fps, temp_audiofile="temp-audio.m4a", remove_temp=True,
            codec="libx264", audio_codec="aac")

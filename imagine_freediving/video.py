from moviepy.editor import ColorClip, CompositeVideoClip, TextClip
from imagine_freediving.overlays.dive_telemetry import DefaultDiveTelemetryOverlay


def generate_dive_video(size, x_points, y_points, annotations, theme, fps):
    duration = x_points[-1]
    background_clip = ColorClip(size, duration=duration, color=theme['bg'])

    # overlay
    w, h = size
    oh = int(h * 0.25)
    overlay_clip = DefaultDiveTelemetryOverlay(x_points, y_points, (w, oh), theme, fps).make_clip()
    # adjust position based on size
    overlay_clip = overlay_clip.set_position((0, h - oh))

    main_clip = CompositeVideoClip([
        background_clip,
        overlay_clip,
    ])

    # add annotations
    annotation_texts = [
        TextClip(text, color="white", fontsize=30, font="Arial")
        .set_position(("center", "center")).set_duration(1).set_start(t)
        for text, (t, f) in annotations
    ]
    main_clip = CompositeVideoClip([
                                       main_clip
                                   ] + annotation_texts)

    return main_clip


def generate_rest_video(size, duration, annotations, theme):
    background_clip = ColorClip(size, duration=duration, color=theme['bg'])
    annotation_texts = [
        TextClip(text, color="white", fontsize=30, font="Arial")
        .set_position(("center", "center")).set_duration(1).set_start(t)
        for text, t in annotations
    ]
    main_clip = CompositeVideoClip([
                                       background_clip
                                   ] + annotation_texts)
    return main_clip

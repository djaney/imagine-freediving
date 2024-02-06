from moviepy.editor import VideoClip, ColorClip, CompositeVideoClip, TextClip
from PIL import Image, ImageDraw
from moviepy.video.io.bindings import PIL_to_npimage
import numpy as np


def generate_video(size, x_points, y_points, annotations, theme, fps):
    duration = x_points[-1]
    background_clip = ColorClip(size, duration=duration, color=theme['bg'])

    # seek_base_clip = ColorClip(size, duration=duration, color=theme['overlay'])
    seek_clip = ColorClip(size, duration=duration, color=theme['overlay'])

    # overlay
    w, h = size
    oh = int(h*0.25)
    # height is 1/4 of screen
    overlay_maker = OverlayMaker(x_points, y_points, (w, oh), theme, fps)
    seek_mask = VideoClip(overlay_maker.make_seek_mask, duration=duration, ismask=True)
    # seek_base_mask = VideoClip(graph.make_seek_base_mask, duration=duration, ismask=True)
    overlay_clip = CompositeVideoClip([
        # seek_base_clip.set_mask(seek_base_mask),
        seek_clip.set_mask(seek_mask),
    ])
    # adjust position based on size
    overlay_clip = overlay_clip.set_position((0, h-oh))
    # set to be transparent
    overlay_clip = overlay_clip.set_opacity(0.6)

    main_clip = CompositeVideoClip([
        background_clip,
        overlay_clip,
    ])

    for text, (t, f) in annotations:
        txt = TextClip(text, color="white", fontsize=30, font="Arial")
        txt = txt.set_position(("center", "center")).set_duration(1).set_start(t)
        main_clip = CompositeVideoClip([
            main_clip, txt
        ])

    return main_clip


class OverlayMaker(object):
    def __init__(self, x_points, y_points, size, theme, fps):
        self.size = size

        self.duration = x_points[-1]
        seeker_resolution = min(int(self.duration * fps), self.size[0])
        self.scale = seeker_resolution / self.duration
        self.x_points_filled = np.linspace(x_points[0], x_points[-1], seeker_resolution)
        self.y_points_interp = np.interp(self.x_points_filled, x_points, y_points) * -1
        self.data_count = len(self.x_points_filled)

        # fix scale
        max_height = int(np.max(self.y_points_interp))
        height_scale = self.size[1] / max_height
        self.x_points_filled *= self.scale
        self.y_points_interp *= height_scale

    def make_seek_mask(self, t):
        return self.make(t, seek_mask=True)

    def make_seek_base_mask(self, t):
        return self.make(t, seek_mask=False)

    def make(self, t, seek_mask=False):
        img = Image.new("1", self.size, 0)
        c = ImageDraw.Draw(img)
        seek = int((t / self.duration) * self.data_count)
        kwargs = {
            "fill": 1,
            "outline": 0,
            "width": 0
        }
        if seek == self.data_count or not seek_mask:
            c.polygon(list(zip(self.x_points_filled, self.y_points_interp)), **kwargs)
        elif seek > 1:
            x_seek = self.x_points_filled[:seek]
            y_seek = self.y_points_interp[:seek]
            x_seek = np.append(x_seek, x_seek[-1:])
            y_seek = np.append(y_seek, [0])
            c.polygon(list(zip(x_seek, y_seek)), **kwargs)

        return PIL_to_npimage(img)

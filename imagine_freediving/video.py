from moviepy.editor import VideoClip, ColorClip, CompositeVideoClip
from PIL import Image, ImageDraw
from moviepy.video.io.bindings import PIL_to_npimage
import numpy as np


def generate_video(size, x_points, y_points, annotations, theme, fps):
    duration = x_points[-1]
    background_clip = ColorClip(size, duration=duration, color=theme['bg'])

    seek_base_clip = ColorClip(size, duration=duration, color=theme['color1'])
    seek_clip = ColorClip(size, duration=duration, color=theme['color1'])

    graph = GraphMaker(x_points, y_points, size, theme, fps)
    seek_mask = VideoClip(graph.make_seek_mask, duration=duration, ismask=True)
    seek_base_mask = VideoClip(graph.make_seek_base_mask, duration=duration, ismask=True)

    main_clip = CompositeVideoClip([
        background_clip,
        seek_base_clip.set_mask(seek_base_mask),
        seek_clip.set_mask(seek_mask),
    ])
    return main_clip


class GraphMaker(object):
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
        img = Image.new("I", self.size, 0)
        c = ImageDraw.Draw(img)
        seek = int((t / self.duration) * self.data_count)
        kwargs = {
            "fill": 100 if seek_mask else 200,
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

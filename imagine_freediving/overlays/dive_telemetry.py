from moviepy.editor import VideoClip, ColorClip, CompositeVideoClip
from PIL import Image, ImageDraw
from moviepy.video.io.bindings import PIL_to_npimage
import numpy as np


class DefaultDiveTelemetryOverlay(object):
    def __init__(self, x_points, y_points, size, theme, fps):
        self.size = size
        self.pad = (10, 10)
        self.theme = theme
        self.duration = x_points[-1]
        seeker_resolution = min(int(self.duration * fps), self.size[0])
        self.scale = (seeker_resolution - self.pad[1] * 2) / self.duration
        self.x_points_filled = np.linspace(x_points[0], x_points[-1], seeker_resolution)
        self.y_points_interp = np.interp(self.x_points_filled, x_points, y_points) * -1
        self.data_count = len(self.x_points_filled)


        # fix scale
        max_height = np.max(self.y_points_interp)
        height_scale = (self.size[1] - self.pad[1] * 2) / max_height
        self.x_points_filled *= self.scale
        self.y_points_interp *= height_scale

    def animate_seeker(self, t, size, is_base):
        super_sampling = 2
        img = Image.new("L", (size[0] * super_sampling, size[1] * super_sampling), 0)
        c = ImageDraw.Draw(img)
        seek = int((t / self.duration) * self.data_count)
        kwargs = {
            "fill": 100 if is_base else 200,
            "outline": 0,
            "width": 0
        }
        if seek == self.data_count or is_base:
            c.polygon(list(zip(self.x_points_filled*super_sampling, self.y_points_interp*super_sampling)), **kwargs)
        elif seek > 1:
            x_seek = self.x_points_filled[:seek]
            y_seek = self.y_points_interp[:seek]
            x_seek = np.append(x_seek, x_seek[-1:])
            y_seek = np.append(y_seek, [0])
            c.polygon(list(zip(x_seek*super_sampling, y_seek*super_sampling)), **kwargs)

        img = img.resize(size=size, resample=Image.LANCZOS)

        return PIL_to_npimage(img) / 255

    def get_animation_function(self, size):
        backdrop = PIL_to_npimage(Image.new("F", size, 1))
        pad = self.pad

        def _make(t):
            base = self.animate_seeker(t, (size[0]-pad[0]*2, size[1]-pad[1]*2), is_base=True)
            seeker = self.animate_seeker(t, (size[0]-pad[0]*2, size[1]-pad[1]*2), is_base=False)
            combined = np.pad(base, (pad, pad), constant_values=0) * 0.25 + \
                np.pad(seeker, (pad, pad), constant_values=0) * 0.25 + \
                backdrop * 0.5
            return combined * 0.7
        return _make

    def make_seeker(self, size):
        seek_clip = ColorClip(size, duration=self.duration, color=self.theme['overlay'])
        seek_mask = VideoClip(self.get_animation_function(size), duration=self.duration, ismask=True)
        return seek_clip.set_mask(seek_mask)

    def make_clip(self):
        return CompositeVideoClip([
            self.make_seeker(self.size),
        ])


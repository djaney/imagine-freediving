from moviepy.editor import VideoClip, ColorClip, CompositeVideoClip
from PIL import Image, ImageDraw
from moviepy.video.io.bindings import PIL_to_npimage
import numpy as np


class DefaultDiveTelemetryOverlay(object):
    def __init__(self, x_points, y_points, size, theme, fps):
        self.size = size
        self.theme = theme
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

    def get_animation_function(self, is_base):
        def _make(t):
            img = Image.new("1", self.size, 0)
            c = ImageDraw.Draw(img)
            seek = int((t / self.duration) * self.data_count)
            kwargs = {
                "fill": 1,
                "outline": 0,
                "width": 0
            }
            if seek == self.data_count or is_base:
                c.polygon(list(zip(self.x_points_filled, self.y_points_interp)), **kwargs)
            elif seek > 1:
                x_seek = self.x_points_filled[:seek]
                y_seek = self.y_points_interp[:seek]
                x_seek = np.append(x_seek, x_seek[-1:])
                y_seek = np.append(y_seek, [0])
                c.polygon(list(zip(x_seek, y_seek)), **kwargs)

            return PIL_to_npimage(img)

        return _make

    def make_seeker(self, is_base):
        seek_clip = ColorClip(self.size, duration=self.duration, color=self.theme['overlay'])
        seek_mask = VideoClip(self.get_animation_function(is_base), duration=self.duration, ismask=True)
        return seek_clip.set_mask(seek_mask)

    def make_clip(self):
        return CompositeVideoClip([
            self.make_seeker(True).set_opacity(0.3),
            self.make_seeker(False).set_opacity(0.6),
        ])


class LineDiveTelemetryOverlay(DefaultDiveTelemetryOverlay):
    def get_animation_function(self, is_base):

        def _make(t):
            img = Image.new("1", self.size, 0)
            c = ImageDraw.Draw(img)
            seek = int((t / self.duration) * self.data_count)
            kwargs = {
                "fill": 1,
                "outline": 0,
                "width": 0
            }
            if seek == self.data_count or is_base:
                self._draw_line(c, self.x_points_filled, self.y_points_interp)
            elif seek > 1:
                x_seek = self.x_points_filled[:seek]
                y_seek = self.y_points_interp[:seek]
                self._draw_line(c, x_seek, y_seek)

            return PIL_to_npimage(img)

        return _make

    def _draw_line(self, c, x_points, y_points):
        c.line(list(zip(x_points, y_points)), fill=1, width=2)


from moviepy.editor import TextClip, ImageClip, CompositeVideoClip
from moviepy.video.io.bindings import PIL_to_npimage
from PIL import Image


class Label(object):
    def __init__(self, pos, size, text, font_size, theme):
        self.pos = pos
        self.size = size
        self.text = text
        self.font_size = font_size
        self.theme = theme

    def make_clip(self):
        txt = TextClip(self.text, font=self.theme['font'], color='white', fontsize=self.font_size)
        txt = txt.set_position(self.pos)

        txt_col = txt.on_color(size=self.size, color=(0, 0, 0), pos=(self.font_size, "center"), col_opacity=0.6)
        txt_clip = txt_col.set_pos(self.pos)
        return txt_clip

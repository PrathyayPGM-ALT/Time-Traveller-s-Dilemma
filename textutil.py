"""Text helpers: word-wrapping and a reusable typewriter timer."""


def is_shouty(text):
    """True for aggressive / shouted lines (mostly uppercase) — they get the
    Undertale-style shaky text treatment."""
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 6:
        return False
    upper = sum(1 for c in letters if c.isupper())
    return upper / len(letters) > 0.6


def wrap_text(text, font, max_width):
    """Wrap *text* to *max_width* px, honouring explicit newlines."""
    out = []
    for para in text.split("\n"):
        if para == "":
            out.append("")
            continue
        cur = ""
        for word in para.split(" "):
            test = (cur + " " + word).strip()
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    out.append(cur)
                cur = word
        out.append(cur)
    return out


class Typewriter:
    """Reveals a string over time at *cps* characters per second."""

    def __init__(self, text, cps=42):
        self.text = text
        self.cps = cps
        self.t = 0.0

    def update(self, dt_ms):
        self.t += dt_ms / 1000.0

    @property
    def count(self):
        return int(self.t * self.cps)

    @property
    def visible(self):
        return self.text[: self.count]

    @property
    def done(self):
        return self.count >= len(self.text)

    def finish(self):
        # Jump straight to fully-revealed.
        self.t = len(self.text) / self.cps + 1.0

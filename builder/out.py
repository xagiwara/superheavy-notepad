import io
from tqdm import tqdm


class TqdmTextIO(io.TextIOBase):
    def write(self, x):
        tqdm.write(x, end="")
        return len(x)


tqdmout = TqdmTextIO()

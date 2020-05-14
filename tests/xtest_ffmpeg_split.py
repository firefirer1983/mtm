import os

from mtm.components.splitter import split_audio

if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    split_audio(root_dir + "/" + "test.mp3", 50, "out/test_{:04d}.mp3")

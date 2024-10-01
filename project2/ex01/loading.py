import time
from time import sleep


def ft_progress(lst: range) -> None:
    total_iterations = len(lst)
    bar_length = 64
    start_time = time.time()

    for i, _ in enumerate(lst):
        elapsed_time = time.time() - start_time
        progress = (i + 1) / total_iterations
        eta = elapsed_time / progress - elapsed_time
        filled_length = int(bar_length * progress)
        bar = "=" * filled_length + ">" + " " * (bar_length - filled_length - 1)

        print(
            f"ETA: {eta:.2f}s | {progress * 100:.0f}%|{bar}| {i + 1}/{total_iterations} | elapsed time {elapsed_time:.2f}s",
            end="\r",
        )
        sleep(0.01)
        yield i

"""Terminal spinner for showing progress."""

import itertools
import sys
import threading
import time

CLEAR_LINE = "\033[2K"


class Spinner:
    """A simple terminal spinner for showing progress."""

    def __init__(self, message: str, inline: bool = False) -> None:
        self._message = message
        self._inline = inline
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._start_time: float = 0
        self._last_len: int = 0

    def _spin(self) -> None:
        chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        while not self._stop_event.is_set():
            text = f"[{self._message} {next(chars)}]"
            if self._inline:
                if self._last_len > 0:
                    sys.stdout.write("\b" * self._last_len)
                sys.stdout.write(text)
                self._last_len = len(text)
            else:
                sys.stdout.write(f"\r{CLEAR_LINE}{text}")
            sys.stdout.flush()
            time.sleep(0.1)

    def start(self) -> None:
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._spin)
        self._thread.start()

    def stop(self, final_message: str, newline: bool = True) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        elapsed = time.time() - self._start_time
        final_text = f"[{final_message} {elapsed:.1f}s]"

        if self._inline:
            if self._last_len > 0:
                sys.stdout.write("\b" * self._last_len)
                sys.stdout.write(" " * self._last_len)
                sys.stdout.write("\b" * self._last_len)
            sys.stdout.write(final_text)
        else:
            sys.stdout.write(f"\r{CLEAR_LINE}{final_text}")

        if newline:
            sys.stdout.write("\n")
        sys.stdout.flush()

"""Capture browser session video from Selenium screenshots (works in headed/headless)."""

from __future__ import annotations

import io
import logging
import re
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class VideoRecorder:
    """Records test execution by sampling WebDriver screenshots into an MP4 file."""

    def __init__(
        self,
        driver: WebDriver,
        output_dir: str | Path,
        test_name: str,
        fps: int = 8,
    ) -> None:
        self._driver = driver
        self._fps = max(1, fps)
        self._frames: list[np.ndarray] = []
        self._stop_event = threading.Event()
        self._driver_lock = threading.Lock()
        self._thread: threading.Thread | None = None

        directory = Path(output_dir).resolve()
        directory.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^\w\-]+", "_", test_name)[:40]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._output_path = (directory / f"{safe_name}_{timestamp}.mp4").resolve()
        self._frames_dir: Path | None = None

    @property
    def output_path(self) -> Path:
        return self._output_path

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._capture_loop,
            name="video-recorder",
            daemon=True,
        )
        self._thread.start()
        logger.info("Video recording started: %s", self._output_path)

    def _capture_loop(self) -> None:
        interval = 1.0 / self._fps
        while not self._stop_event.is_set():
            try:
                with self._driver_lock:
                    png = self._driver.get_screenshot_as_png()
                image = Image.open(io.BytesIO(png)).convert("RGB")
                self._frames.append(np.asarray(image))
            except Exception as exc:
                logger.debug("Frame capture skipped: %s", exc)
            self._stop_event.wait(interval)

    def _encode_with_ffmpeg(self) -> None:
        self._frames_dir = Path(tempfile.mkdtemp(prefix="vidframes_"))
        try:
            for index, frame in enumerate(self._frames):
                frame_path = self._frames_dir / f"f{index:05d}.png"
                imageio.imwrite(frame_path, frame)

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            command = [
                ffmpeg,
                "-y",
                "-framerate",
                str(self._fps),
                "-i",
                str(self._frames_dir / "f%05d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(self._output_path),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
        finally:
            if self._frames_dir is not None:
                shutil.rmtree(self._frames_dir, ignore_errors=True)
                self._frames_dir = None

    def stop_and_save(self) -> Path | None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=10)

        if not self._frames:
            logger.warning("No frames captured for video: %s", self._output_path)
            return None

        try:
            self._encode_with_ffmpeg()
            if not self._output_path.is_file() or self._output_path.stat().st_size == 0:
                logger.error("Video file was not written: %s", self._output_path)
                return None
            logger.info(
                "Video saved: %s (%s frames)",
                self._output_path,
                len(self._frames),
            )
            return self._output_path
        except subprocess.CalledProcessError as exc:
            logger.error(
                "FFmpeg failed for %s: %s",
                self._output_path,
                exc.stderr or exc,
            )
            return None
        except Exception as exc:
            logger.error("Failed to save video %s: %s", self._output_path, exc)
            return None

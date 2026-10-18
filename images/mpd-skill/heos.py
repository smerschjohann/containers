# -*- coding: utf-8 -*-
"""
HEOS CLI Client for controlling Denon / Marantz AVR receivers over network (port 1255).
"""

import json
import socket
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


def send_command(host: str, command: str, port: int = 1255, timeout: float = 3.0) -> Optional[Dict[str, Any]]:
    """
    Send a raw HEOS CLI command and parse the JSON response.
    HEOS protocol uses JSON-like text lines terminated by \\r\\n.
    """
    if not host:
        return None

    cmd_str = command.strip()
    if not cmd_str.endswith("\r\n"):
        cmd_str += "\r\n"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            s.sendall(cmd_str.encode("utf-8"))

            data = b""
            while b"\r\n" not in data:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk

            first_line = data.split(b"\r\n")[0]
            if first_line:
                parsed = json.loads(first_line.decode("utf-8"))
                logger.debug("HEOS response for %s: %s", command.strip(), parsed)
                return parsed
    except Exception as e:
        logger.error("HEOS communication error with %s:%s: %s", host, port, e)

    return None


def get_players(host: str, port: int = 1255, timeout: float = 3.0) -> List[Dict[str, Any]]:
    """Query list of available HEOS players on the receiver."""
    resp = send_command(host, "heos://player/get_players", port=port, timeout=timeout)
    if resp and resp.get("heos", {}).get("result") == "success":
        payload = resp.get("payload")
        if isinstance(payload, list):
            return payload
    return []


def resolve_player_id(host: str, pid: Optional[int] = None, port: int = 1255, timeout: float = 3.0) -> Optional[int]:
    """Return configured pid, or automatically discover the first player's pid."""
    if pid is not None:
        return int(pid)

    players = get_players(host, port=port, timeout=timeout)
    if players:
        chosen = players[0]
        resolved_pid = chosen.get("pid")
        logger.info("Auto-discovered HEOS player: %s (PID: %s)", chosen.get("name"), resolved_pid)
        return resolved_pid

    logger.warning("No HEOS players found on %s:%s", host, port)
    return None


def play_stream(host: str, stream_url: str, pid: Optional[int] = None, port: int = 1255, timeout: float = 3.0) -> bool:
    """
    Direct the HEOS player to play an audio stream URL (HTTP radio / FLAC stream).
    The AVR powers on and switches to HEOS input automatically.
    """
    target_pid = resolve_player_id(host, pid=pid, port=port, timeout=timeout)
    if target_pid is None:
        logger.error("Cannot play stream: unable to determine HEOS player PID on %s", host)
        return False

    cmd = f"heos://browse/play_stream?pid={target_pid}&url={stream_url}"
    logger.info("Sending stream to HEOS on %s (PID: %s): %s", host, target_pid, stream_url)
    resp = send_command(host, cmd, port=port, timeout=timeout)

    if resp and resp.get("heos", {}).get("result") == "success":
        return True

    logger.warning("HEOS play_stream returned non-success: %s", resp)
    return False


def set_play_state(host: str, state: str, pid: Optional[int] = None, port: int = 1255, timeout: float = 3.0) -> bool:
    """Set player playback state: 'play', 'pause', or 'stop'."""
    target_pid = resolve_player_id(host, pid=pid, port=port, timeout=timeout)
    if target_pid is None:
        return False

    cmd = f"heos://player/set_play_state?pid={target_pid}&state={state}"
    resp = send_command(host, cmd, port=port, timeout=timeout)
    return bool(resp and resp.get("heos", {}).get("result") == "success")


def stop(host: str, pid: Optional[int] = None, port: int = 1255, timeout: float = 3.0) -> bool:
    """Stop HEOS playback."""
    return set_play_state(host, "stop", pid=pid, port=port, timeout=timeout)


def pause(host: str, pid: Optional[int] = None, port: int = 1255, timeout: float = 3.0) -> bool:
    """Pause HEOS playback."""
    return set_play_state(host, "pause", pid=pid, port=port, timeout=timeout)


def resume(host: str, pid: Optional[int] = None, port: int = 1255, timeout: float = 3.0) -> bool:
    """Resume HEOS playback."""
    return set_play_state(host, "play", pid=pid, port=port, timeout=timeout)

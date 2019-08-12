#!/usr/bin/env python3
from contextlib import contextmanager
from typing import Optional, List, Union

import serial


class CommandError(Exception):
    pass


class CommandTemporarilyInvalidError(Exception):
    pass


class Uniden:
    VOLUME = "VOL"
    SQUELCH = "SQL"
    SCREEN = "STS"
    MODEL = "MDL"
    VERSION = "VER"
    OK = "OK"
    ERROR = "ERR"
    WRONG_MODE = "NG"
    ENTER_PROGRAM = "PRG"
    EXIT_PROGRAM = "EPG"
    KEY = "KEY"
    CHARGE_TIME = "BSV"
    CLEAR_MEMORY = "CLR"
    CHANNEL_SETTINGS = "CIN"

    def __init__(self):
        self._serial = None
        self._volume = None
        self._squelch = None
        self._channels = {}

    @property
    def volume(self) -> int:
        if self._volume is None:
            self._volume = int(self._execute(Uniden.VOLUME)[0])
        return self._volume

    @volume.setter
    def volume(self, value: int) -> None:
        self._volume = value
        self._execute(Uniden.VOLUME, [str(value)])

    @property
    def squelch(self) -> int:
        if self._squelch is None:
            self._squelch = int(self._execute(Uniden.SQUELCH)[0])
        return self._squelch

    @squelch.setter
    def squelch(self, value: int) -> None:
        self._squelch = value
        self._execute(Uniden.SQUELCH, [str(value)])

    def get_channel(self, channel_id: int):
        with self._program_mode():
            channel = self._execute(Uniden.CHANNEL_SETTINGS, [str(channel_id)])
        self._channels[channel_id] = channel
        return channel

    def set_channel(self, channel_id: int, stuff) -> None:  # TODO a lot of arguments needed
        raise NotImplementedError

    def get_screen(self):
        with self._program_mode():
            screen = self._execute(Uniden.SCREEN)
        return screen  # TODO there is a lot to parse

    @contextmanager
    def _program_mode(self):
        self._execute(Uniden.ENTER_PROGRAM)
        yield
        self._execute(Uniden.EXIT_PROGRAM)
        # TODO un-hold scanner?
        # KEY,H,P

    def _get_scanner_info(self) -> None:
        self.model = self._execute(Uniden.MODEL)[0]
        self.software_version = self._execute(Uniden.VERSION)[0]

    def _execute(self, command: str, parameters: Optional[List[str]] = None) -> Union[List[str], bool]:
        if parameters:
            scanner_command = command.encode() + b"," + ",".join(parameters).encode() + b"\r"
        else:
            scanner_command = command.encode() + b"\r"
        self._serial.write(scanner_command)
        response = self._serial.readline().strip().split(b",")  # TODO those are bytes...
        if response[0] == Uniden.ERROR:
            raise CommandError(f"Scanner returned error while executing command {command}")
        response = response[1:]
        if response[0] == Uniden.WRONG_MODE:
            raise CommandTemporarilyInvalidError(f"Scanner cannot execute command {command} in current mode")
        elif response[0] == Uniden.OK:
            return True

        return response

    def connect(self, serial_port: str) -> None:
        self._serial = serial.Serial(serial_port, 460800, timeout=0.1)
        self._get_scanner_info()

    def disconnect(self) -> None:
        self._serial.close()


if __name__ == "__main__":
    un = Uniden()
    un.connect("/dev/ttyACM0")
    breakpoint()

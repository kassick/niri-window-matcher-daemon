# SPDX-License-Identifier: LGPL-3.0-or-later
# This file is part of niri-window-matcher.
#
# niri-window-matcher is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# niri-window-matcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with niri-window-matcher.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
from socket import AF_UNIX, SHUT_WR, socket
import subprocess
from typing import (
    Type,
    TypeVar,
)

from niri_window_matcher.logger import logger

OutType = TypeVar("OutType")


def niri_json_from_msg(*msg: str, type: Type[OutType] = list) -> OutType:
    proc = subprocess.Popen(["niri", "msg", "--json", *msg], stdout=subprocess.PIPE)
    proc.wait()
    if proc.returncode != 0:
        raise Exception(f"niri returned non-zero status {proc.returncode}")

    if not proc.stdout:
        raise Exception("No output from niri")

    output = json.loads(proc.stdout.read())

    return output


def niri_event_stream():
    niri_socket = socket(AF_UNIX)
    niri_socket.connect(os.environ["NIRI_SOCKET"])
    file = niri_socket.makefile("rw")

    _ = file.write('"EventStream"')
    file.flush()
    niri_socket.shutdown(SHUT_WR)

    return file


def niri_socket_send_msg(request):
    logger.debug(f"Sending {request}")
    with socket(AF_UNIX) as niri_socket:
        niri_socket.connect(os.environ["NIRI_SOCKET"])
        #niri_socket.sendall(f"{json.dumps(request)}\n")
        file = niri_socket.makefile("rw")
        _ = file.write(json.dumps(request)+ "\n")
        file.flush()
        response = file.readline()
        return json.loads(response)

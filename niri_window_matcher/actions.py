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

from niri_window_matcher.logger import logger
from niri_window_matcher.niri_comm import niri_socket_send_msg
from niri_window_matcher.niri_types import NiriState, WindowEntryDict


def resize_to_output(
    niri_state: NiriState,
    window: WindowEntryDict,
):
    logger.info("Resizing window %d \"%s\" to 100%%", window["id"], window["title"])
    response = niri_socket_send_msg(
        {
            "Action": {
                "SetWindowWidth": {
                    "id": window["id"],
                    "change": {"SetProportion": 100.0},
                }
            }
        }
    )
    logger.debug("Response (width): %s", response)

    response = niri_socket_send_msg(
        {
            "Action": {
                "SetWindowHeight": {
                    "id": window["id"],
                    "change": {"SetProportion": 100.0},
                }
            }
        }
    )
    logger.debug("Response (height): %s", response)


def make_float(id: int):
    niri_socket_send_msg({"Action": {"MoveWindowToFloating": {"id": id}}})

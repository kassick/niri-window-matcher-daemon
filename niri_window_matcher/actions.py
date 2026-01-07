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

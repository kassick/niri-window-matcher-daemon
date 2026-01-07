from niri_window_matcher.niri_comm import niri_socket_send_msg
from niri_window_matcher.niri_types import NiriState, WindowEntryDict


def resize_to_output(
    niri_state: NiriState,
    window: WindowEntryDict,
    side_panel_widths: int,
    top_bottom_panel_heights: int,
):
    if not (output := niri_state.find_output_of(window)):
        print("output of window not found")
        return

    output_width = output["logical"]["width"]
    output_height = output["logical"]["height"]

    niri_socket_send_msg(
        {
            "Action": {
                "SetWindowWidth": {"id": window["id"], "change": {"SetProportion": 100.0}}
            }
        }
    )
    niri_socket_send_msg(
        {
            "Action": {
                "SetWindowHeight": {
                    "id": window["id"],
                    "change": {"SetProportion": 100.0},
                }
            }
        }
    )


def make_float(id: int):
    niri_socket_send_msg({"Action": {"MoveWindowToFloating": {"id": id}}})

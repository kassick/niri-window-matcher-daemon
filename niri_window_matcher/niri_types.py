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

from dataclasses import dataclass, field
from functools import cached_property
from typing import (
    Mapping,
    NotRequired,
    Tuple,
    TypedDict,
)

from niri_window_matcher.niri_comm import niri_json_from_msg

WindowId = int
WorkspaceId = int
OutputId = str


class WindowLayoutDict(TypedDict):
    pos_in_scrolling_layout: Tuple[int, int]
    tile_size: Tuple[float, float]
    window_size: Tuple[int, int]


class WindowEntryDict(TypedDict):
    id: int
    title: str
    app_id: str
    workspace_id: int
    is_focused: bool
    is_floating: bool
    is_urgent: NotRequired[bool]

    layout: WindowLayoutDict

    _matched: NotRequired[bool]


class WorkspaceEntryDict(TypedDict):
    id: int
    idx: int
    name: NotRequired[str]
    output: str
    is_active: bool
    is_focused: bool
    active_window_id: int


class OutputLogicalDimensionsDict(TypedDict):
    width: int
    height: int


class OutputEntryDict(TypedDict):
    name: str
    logical: OutputLogicalDimensionsDict

@dataclass
class NiriState:
    windows: dict[WindowId, WindowEntryDict] = field(default_factory=dict)
    workspaces: dict[WorkspaceId, WorkspaceEntryDict] = field(default_factory=dict)
    outputs: Mapping[OutputId, OutputEntryDict] = field(default_factory=dict)

    def refresh_outputs(self):
        self.outputs = niri_json_from_msg("outputs", type=Mapping[OutputId, OutputEntryDict])

    def find_output_of(self, window: WindowEntryDict) -> OutputEntryDict | None:
        if not (workspace := self.workspaces.get(window["workspace_id"])):
            return None

        return self.outputs.get(workspace["output"])

    def add_window(self, window: WindowEntryDict):
        self.windows[window["id"]] = window

    def remove_window(self, window_id: WindowId):
        try:
            del self.windows[window_id]
        except KeyError:
            pass

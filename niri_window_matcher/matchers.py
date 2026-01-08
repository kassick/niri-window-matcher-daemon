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

from ast import TypeVar
from dataclasses import dataclass, field
import re
from typing import (
    Any,
    Callable,
    Protocol,
    Self,
    Sequence,
    Type,
    Union,
)

from niri_window_matcher.niri_types import NiriState, WindowEntryDict

Result = TypeVar("Result")


# def _class_or_instance[Result](obj: Result | Type[Result]) -> Result:
#     if isinstance(obj, type):
#         return obj()  # type: ignore
#     return obj


class Matcher:
    def matches(self, niri_state: NiriState, window: WindowEntryDict) -> bool: ...

    def __and__(self, other: "Matcher"):
        return AndMatcher(self, other)

    def __or__(self, other: "Matcher"):
        return OrMatcher(self, other)

    def __invert__(self):
        return NotMatcher(self)


class _ConstTrueMatcher(Matcher):
    def matches(self, niri_state, window):
        return True


ConstTrueMatcher = _ConstTrueMatcher()


class _ConstFalseMatcher(Matcher):
    def matches(self, niri_state, window):
        return False


ConstFalseMatcher = _ConstFalseMatcher()


@dataclass
class NotMatcher(Matcher):
    matcher: Matcher

    def matches(self, niri_state, window):
        return not self.matcher.matches(niri_state, window)


@dataclass
class AndMatcher(Matcher):
    left: Matcher
    right: Matcher

    def matches(self, niri_state, window):
        return (
            #
            self.left.matches(niri_state, window)
            and
            #
            self.right.matches(niri_state, window)
        )


@dataclass
class OrMatcher(Matcher):
    left: Matcher
    right: Matcher

    def matches(self, niri_state, window):
        return (
            #
            self.left.matches(niri_state, window)
            or
            #
            self.right.matches(niri_state, window)
        )


@dataclass(kw_only=True)
class TitleRegexMatch(Matcher):
    title: str

    def matches(self, niri_state, window: WindowEntryDict):
        return bool(self.title) and re.search(self.title, window["title"]) is not None


@dataclass(kw_only=True)
class AppidRegexMatch(Matcher):
    app_id: str

    def matches(self, niri_state, window: WindowEntryDict):
        return (
            bool(self.app_id) and re.search(self.app_id, window["app_id"]) is not None
        )


class _NewWindowMatcher(Matcher):
    def matches(self, niri_state: NiriState, window: WindowEntryDict):
        return window["id"] not in niri_state.windows


NewWindowMatcher = _NewWindowMatcher()


class LargeWindowMatcher(Matcher):
    def __init__(
        self,
        side_panel_widths: int,
        top_bottom_panel_heights: int,
    ):
        self.width_grace = side_panel_widths
        self.height_grace = top_bottom_panel_heights

    def matches(self, niri_state: NiriState, window: WindowEntryDict):
        if not (output := niri_state.find_output_of(window)):
            return False

        output_width = output["logical"]["width"]
        output_height = output["logical"]["height"]

        window_width, window_height = window["layout"]["window_size"]

        return (
            window_width > output_width - self.width_grace
            or window_height > output_height - self.height_grace
        )


class _FloatWindowMatcher(Matcher):
    def matches(self, niri_state: NiriState, window: WindowEntryDict):
        return window["is_floating"]


FloatWindowMatcher = _FloatWindowMatcher()


@dataclass
class Rule:
    match: Matcher = field(default=ConstTrueMatcher)
    exclude: Matcher = field(default=ConstFalseMatcher)

    actions: Sequence[Callable[[NiriState, WindowEntryDict], Any]] = field(
        default_factory=list
    )

    def matches(self, niri_state: NiriState, window: WindowEntryDict):
        return self.match.matches(niri_state, window) and not self.exclude.matches(
            niri_state, window
        )

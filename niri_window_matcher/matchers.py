from dataclasses import dataclass, field
import re
from typing import (
    Any,
    Callable,
    Protocol,
    Sequence,
)

from niri_window_matcher.niri_types import NiriState, WindowEntryDict


class Matcher(Protocol):
    def matches(self, niri_state: NiriState, window: WindowEntryDict) -> bool: ...


class AlwaysMatches:
    def matches(self, niri_state, window: WindowEntryDict):
        return True


@dataclass
class MatchesAll:
    matchers: Sequence[Matcher]

    def matches(self, niri_state, window):
        return all(matcher.matches(niri_state, window) for matcher in self.matchers)


@dataclass(kw_only=True)
class TitleRegexMatch:
    title: str

    def matches(self, niri_state, window: WindowEntryDict):
        return self.title and re.search(self.title, window["title"]) is not None


@dataclass(kw_only=True)
class AppidRegexMatch:
    app_id: str

    def matches(self, niri_state, window: WindowEntryDict):
        return self.app_id and re.search(self.app_id, window["app_id"]) is not None


class NewWindowMatcher:
    def matches(self, niri_state: NiriState, window: WindowEntryDict):
        return window["id"] not in niri_state.windows


class LargeWindowMatcher:
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


@dataclass
class Rule:
    match: list[Matcher] = field(default_factory=list)
    exclude: list[Matcher] = field(default_factory=list)

    actions: Sequence[Callable[[NiriState, WindowEntryDict], Any]] = field(
        default_factory=list
    )

    def matches(self, niri_state: NiriState, window: WindowEntryDict):
        return (
            # Any matcher may approve the rule
            any(m.matches(niri_state, window) for m in self.match)
            and
            # If any exclude rule matches, ignore it
            all(not m.matches(niri_state, window) for m in self.exclude)
        )

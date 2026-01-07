#!/usr/bin/python3
"""
Based on https://github.com/YaLTeR/niri/discussions/1599

Like open-float, but dynamically. Floats a window when it matches the rules.

Some windows don't have the right title and app-id when they open, and only set
them afterward. This script is like open-float for those windows.

Usage: fill in the RULES array below, then run the script.
"""

from functools import partial
import json
from typing import (
    Sequence,
)

from niri_window_matcher.actions import resize_to_output
from niri_window_matcher.matchers import (
    LargeWindowMatcher,
    MatchesAll,
    NewWindowMatcher,
    Rule,
)
from niri_window_matcher.niri_comm import niri_event_stream
from niri_window_matcher.niri_types import (
    NiriState,
    WindowEntryDict,
    WorkspaceEntryDict,
)


# Write your rules here. One Rule() = one window-rule {}.
RULES = [
    Rule(
        match=[
            MatchesAll(
                matchers=[
                    NewWindowMatcher(),
                    LargeWindowMatcher(
                        # These depend on panels -- these values come from my
                        # waybar setup
                        side_panel_widths=49,
                        top_bottom_panel_heights=30,
                    ),
                ]
            )
        ],
        actions=[
            partial(resize_to_output, side_panel_widths=49, top_bottom_panel_heights=30)
        ],
    )
    # window-rule {} with one match.
    # Rule([Match(title="Bitwarden", app_id="firefox")]),
    # window-rule {} with one match and one exclude.
    # Rule(
    #     [Match(title="rs")],
    #     exclude=[Match(app_id="Alacritty")],
    # ),
    # window-rule {} with two matches.
    # Rule(
    #     [
    #         Match(app_id="^foot$"),
    #         Match(app_id="^mpv$"),
    #     ]
    # ),
]


if len(RULES) == 0:
    print("fill in the RULES list, then run the script")
    exit()


def handle_matches(niri_state: NiriState, window: WindowEntryDict) -> bool:
    """Handles a window and returns if any of the rules matched it"""

    # Check if the window has been matched by the rule before and avoid
    # reapplying. Important because during initialization, the script will
    # start with WindowsChanged and an empty window mapping, therefore it will
    # match all opened windows. Afterwards, these windows should not be touched
    # by the same rule. Also, a window may change title after initialization
    # (or some other event that generated WindowOpenedOrChanged) -- if we have
    # already acted on it, we want to avoid handling it again...
    matched_before = False
    if existing_window := niri_state.windows.get(window["id"]):
        matched_before = bool(existing_window.get("_matched"))

    if matched_before:
        # No need to search for matches, it won'd be handled either way
        return True

    if not (matching_rules := [r for r in RULES if r.matches(niri_state, window)]):
        # No matching rule, skip
        return False

    # Handle actions
    for rule in matching_rules:
        print(f"Window {window['id']} matches rule {rule}")
        for action in rule.actions:
            print(f"Performing action {action}")
            action(niri_state, window)

    return True


def handle_single_window_and_update(
    niri_state: NiriState, window: WindowEntryDict
) -> bool:
    matched = handle_matches(niri_state, window)
    # Mark the window with the matching result before storing
    window["_matched"] = matched
    niri_state.add_window(window)

    return matched


def handle_event(niri_state: NiriState, event: dict):
    print(f"event line has keys {event.keys()}")

    if workspaces_changed := event.get("WorkspacesChanged"):
        # First event is always WorkspaceChanged. Also, when outputs are connected
        # or disconnected, a WorkspaceChanged event will also happen. Take the
        # change to update the local niri state
        print("Handling Workspaces")
        workspace_list: Sequence[WorkspaceEntryDict] = workspaces_changed["workspaces"]
        niri_state.workspaces = {ws["id"]: ws for ws in workspace_list}
        niri_state.refresh_outputs()

    elif windows_changed := event.get("WindowsChanged"):
        # Initialization Event with all windows
        print("Handling Windowschanged")
        window: WindowEntryDict
        for window in windows_changed["windows"]:
            handle_single_window_and_update(niri_state, window)

    elif window_opened_or_changed := event.get("WindowOpenedOrChanged"):
        # New window or some other relevant update
        print("Handling WindowOpenedOrChanged")
        window = window_opened_or_changed["window"]
        handle_single_window_and_update(niri_state, window)

    elif window_closed := event.get("WindowClosed"):
        print("Handling WindowClosed")
        niri_state.remove_window(window_closed["id"])


def main():
    # Initialize the state
    niri_state = NiriState()

    for line in niri_event_stream():
        event: dict = json.loads(line)
        handle_event(niri_state, event)


if __name__ == "__main__":
    main()

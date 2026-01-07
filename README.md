# Niri Window Matcher

A dynamic window rule daemon for the [Niri](https://github.com/YaLTeR/niri) window manager.

## About

This project provides a daemon that applies window rules to new windows dynamically based on customizable matchers. Unlike Niri's built-in window rules, this daemon allows you to match windows based on their runtime properties, which is useful for applications that don't have the correct title or app-id when they first open.

## Features

- **Dynamic Window Matching**: Match windows based on properties like title, app-id, and size
- **Custom Actions**: Define custom actions to execute when a window matches a rule
- **Real-time Processing**: Continuously monitors window events from Niri
- **Flexible Rules**: Combine multiple matchers with include/exclude conditions
- **Built-in Matchers**:
  - `TitleRegexMatch`: Match window title against a regex pattern
  - `AppidRegexMatch`: Match app-id against a regex pattern
  - `NewWindowMatcher`: Match newly opened windows
  - `LargeWindowMatcher`: Match windows that are larger than a threshold
  - `MatchesAll`: Combine multiple matchers (all must match)

## Installation

### Prerequisites

- Python 3.10 or newer
- Niri window manager with event stream support

### From Source

Clone the repository and install:

```bash
git clone <repository-url>
cd niri-window-matcher
pip install -e .
```

## Configuration

Edit the `RULES` array in `niri_window_matcher/__main__.py` to define your window rules. Each rule specifies:

- **match**: A list of matchers that should match the window
- **exclude**: (Optional) A list of matchers that should exclude the window
- **actions**: A list of actions to execute when the rule matches

### Example Configuration

```python
from niri_window_matcher.matchers import (
    LargeWindowMatcher,
    MatchesAll,
    NewWindowMatcher,
    Rule,
    TitleRegexMatch,
    AppidRegexMatch,
)
from niri_window_matcher.actions import resize_to_output

RULES = [
    # Float new windows larger than the output (accounting for panels)
    Rule(
        match=[
            MatchesAll(
                matchers=[
                    NewWindowMatcher(),
                    LargeWindowMatcher(
                        side_panel_widths=49,
                        top_bottom_panel_heights=30,
                    ),
                ]
            )
        ],
        actions=[resize_to_output],
    ),
    # Match Firefox windows by title and app-id
    Rule(
        match=[
            MatchesAll(
                matchers=[
                    TitleRegexMatch(title="Bitwarden"),
                    AppidRegexMatch(app_id="firefox"),
                ]
            )
        ],
        actions=[some_action],
    ),
]
```

## Usage

Run the daemon:

```bash
niri-window-matcher-daemon
```

For debugging, you can enable debug logging by setting the `LOG_LEVEL` environment variable:

```bash
LOG_LEVEL=DEBUG niri-window-matcher-daemon
```

## How It Works

The daemon:

1. Connects to Niri's event stream
2. Listens for window events (new windows, window changes, etc.)
3. For each window, checks all configured rules
4. Executes actions for rules that match
5. Tracks which windows have been matched to avoid reapplying rules

This approach is particularly useful for windows that set their title or app-id after opening, allowing you to write rules that depend on final window properties rather than initial ones.

## Related

Based on [Niri Discussion #1599](https://github.com/YaLTeR/niri/discussions/1599)

## License

LGPL -- https://www.gnu.org/licenses/lgpl-3.0.en.html

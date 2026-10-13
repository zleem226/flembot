# Friends O' Flembot site

The public website for the Friends O' Flembot fantasy football league, served by GitHub Pages
from the `main` branch root at https://zleem226.github.io/flembot.

## THIS REPO IS PUBLIC

Everything committed here can be read by anyone on the internet. Never commit:
- weekly recap emails or their text (they stay in Gmail, league-only)
- email addresses, phone numbers or anything personal about league members beyond first names and team names
- draft tools, cheat sheets, keeper analysis or auction strategy
- anything about the commissioner's job or family

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | Hall of Champions: champions, dynasty rankings, record book, 2025 season, shame. Hand-edited. Its nav has a "2026 Live" link to `2026.html`. |
| `2026.html` | The live 2026 (Season 21) page: standings, schedule luck, weekly scores, best games, goose eggs, timeline. **Generated; don't hand-edit.** |
| `2026-data.json` | All 2026 numbers. `2026.html` fetches it at load time. This is the only file the weekly update changes. |
| `build/dashboard-page.html` | Source for the 2026 page. It is written against the Claude Dashboard `dash` API (`dash.calc`, `dash.data`, `dash.onData`); the builder adds a small stand-in for that API. |
| `build/make_2026_page.py` | Builds `2026.html` from the source. Run `python3 build/make_2026_page.py` from the repo root. |
| `build/vendor/d3.min.js` | d3 v7.9.0 (ISC licence in `d3-LICENSE`), inlined into the page so it has no outside dependencies. |

## 2026-data.json

```
{
  "updated": "<UTC ISO time>",
  "matchups":     [{week, manager, team, opponent, points_for, points_against, result: "W"|"L"}],   // 12 rows per week
  "top_starters": [{player, pos, week, manager, points, line}],   // top 12 starter games, bench excluded
  "goose_eggs":   [{week, player, pos, manager, note}],           // starters who played and scored exactly 0.00
  "timeline":     [{date: "YYYY-MM-DD", phase, event}]            // one short line per event; dates unique
}
```

Standings, all-play records, luck, weekly highs and the season totals are all calculated in the page
from `matchups`; none of them are stored.

Managers (always exactly these 12): Joe, Babo, Alex, Josh, Jason, Zach, Seth, Kevin, Tom, Andrew, Dan, Jon.
Zach is the commissioner.

## Weekly update

A scheduled Claude task ("Flembot weekly dashboard update") runs Tuesdays and Wednesdays at 11:46 AM
America/New_York. It reads the newest sent "2026 Friends O'Flembot Week N Recap" email, adds week N to
`2026-data.json`, and commits it as "Flembot 2026: add Week N". It also mirrors the same data into a
private Claude dashboard.

It publishes only if the week checks out: 12 rows, each manager once, 6 W and 6 L, paired opponents,
and season records and points-for that match the recap's standings table. Otherwise it changes nothing
and reports why.

Manual fix: edit `2026-data.json`, commit, push. No rebuild needed.

## Changing the 2026 page

1. Edit `build/dashboard-page.html`.
2. `python3 build/make_2026_page.py`, then open `2026.html` through a local server
   (`python3 -m http.server`; opening the file directly can't fetch the JSON) and check desktop and phone widths.
3. Commit both files. If the private Claude dashboard should match, its `files/index.html` gets the same source.

## Next season

Copy the pattern: `2027.html` + `2027-data.json`, point the fetch in the builder at the new file name,
and add a nav link in `index.html`.

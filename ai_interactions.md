# AI Interactions Log

This log covers the two stretch challenges. The AI coding assistant was Claude Code (Claude Opus 5.5) running in VS Code, with `src/recommender.py`, `src/main.py`, and `data/songs.csv` open in the workspace.

---

## Challenge 1: Advanced Song Features

### Prompt used

I pasted the challenge text into the assistant's chat:

> Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., "nostalgic," "aggressive," "euphoric"). Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes.

### What the AI generated

**Five new columns in `data/songs.csv`** (values filled in for all 20 songs):

| Column | Type | Example |
|---|---|---|
| `popularity` | 0–100 | Gym Hero = 88, Three AM Blues = 29 |
| `release_decade` | year | 1960 … 2020 |
| `mood_tags` | 3 tags, separated by `\|` | `aggressive\|rebellious\|dark` |
| `instrumentalness` | 0–1 | lofi ≈ 0.9, pop ≈ 0.02 |
| `language` | text | english, spanish, none |

**Scoring changes in `src/recommender.py`:**
- **`load_songs`:** converts the new columns to the right types, and splits `mood_tags` into a list.
- **`score_song`:** adds five new optional checks:
  - decade: +1.0 for the same decade, +0.5 for a neighbouring one
  - mood tags: +0.5 for one shared tag, +1.0 for two or more
  - popularity: up to +0.5 for closeness to the target
  - instrumental fit: up to +0.5
  - language match: +0.5
- **`Song` and `UserProfile`:** new fields with default values, so the existing tests and the four-argument `UserProfile(...)` calls still work.
- **`src/main.py`:** a new **Throwback Explorer** profile that uses the new features.

**Key design decision (the AI's suggestion, which I accepted):** every new feature is **optional**. A song only gets points for, say, decade if the user actually asked for a decade. This kept all 7 existing profiles' results identical, so the earlier evaluation in the README and model card stayed valid.

### Manual verification notes
- **The CSV is still valid.** It has 20 rows and 15 columns, and the original 10 columns are unchanged (`git diff` shows only the new values appended to each row).
- **Old results are unchanged.** `python -m src.main` was compared line by line with the output saved before this change. All 7 original profiles were identical. The only differences were the new "Scoring mode" line and the new Throwback Explorer profile.
- **Hand-checked one score.** Night Drive Loop for Throwback Explorer was reported as 6.04:

  2.00 (genre) + 1.27 (energy 0.75 vs 0.60) + 1.00 (1980s) + 1.00 (two shared tags) + 0.42 (popularity 66 vs 50) + 0.35 (instrumentalness 0.70 × 0.5) = **6.04** ✓
- **The starter tests still pass.** I ran both test functions directly. pytest isn't installed on my machine yet.
- **Something I noticed:** Iron Tempest (metal / angry) reaches Throwback Explorer's top 5 almost entirely because of the 1980s bonus. A single new feature can drag in an unrelated song.
- *(Add your own checks here.)*

---

## Challenge 2: Multiple Scoring Modes

### Prompt used

> Build two or more different ranking strategies (e.g., "Genre-First," "Mood-First," or "Energy-Focused") so a user can switch between modes in main.py. … brainstorm a design pattern (like a simple "Strategy" pattern) that keeps your code modular.

### Brainstorm: options the AI considered

| Option | How it works | Verdict |
|---|---|---|
| 1. `if/elif` on a mode string inside `score_song` | `if mode == "genre_first": genre_points = 4.0 …` | Rejected. Every new mode means editing the scoring function, and the branches would multiply. |
| 2. Full Strategy classes | One class per mode (`GenreFirstStrategy`, …), each with its own `score()` method | Rejected *for now*. All four modes use the same logic and differ only in weights, so separate classes would repeat the same code four times. |
| 3. **Strategy as data** *(chosen)* | One `ScoringMode` object per mode, holding its weights. `score_song` takes a mode and asks it for each weight. | Chosen: modular, no repeated logic, and a new mode is one line. |

### Chosen design

```python
@dataclass(frozen=True)
class ScoringMode:          # the "strategy"
    name: str
    description: str
    genre: float = 2.0
    mood: float = 1.5
    energy: float = 1.5
    ...                     # one weight per feature

SCORING_MODES = {           # registry of available strategies
    "balanced": ScoringMode("balanced", ...),
    "genre_first": ScoringMode("genre_first", ..., genre=4.0, mood=1.0, energy=1.0),
    "mood_first": ScoringMode("mood_first", ..., genre=1.0, mood=3.0, mood_tags=2.0, valence=1.5),
    "energy_focused": ScoringMode("energy_focused", ..., genre=1.0, energy=3.0),
}

score_song(user_prefs, song, mode)        # the "context" that uses a strategy
recommend_songs(user_prefs, songs, k, mode)
```

- **Choosing a mode:** `python -m src.main --mode mood_first`. The `--mode` option only accepts real mode names, and anything else prints an error listing the valid choices.
- **Default:** `balanced` keeps the original weights, so nothing changes unless you ask for a different mode.
- **Frozen dataclass:** a mode can't be changed by accident while it's being used.
- **The class path supports modes too:** `Recommender(songs, mode="genre_first")`.
- **Room to grow:** if a future mode needs genuinely *different logic* rather than different weights, for example a diversity re-ranker, the design can grow into Option 2 without changing how `main.py` chooses a mode.

### How the AI contributed
- **Proposed the three options** and argued for the lightweight "strategy as data" version, pointing out that the four modes only differ in weights.
- **Suggested making `energy_focused` use exactly the weights from my earlier weight-shift experiment.** That experiment can now be reproduced with one command instead of editing code by hand.
- **Wrote the code, then compared all four modes** on three profiles.

### Manual verification notes
- **`energy_focused` reproduces the earlier experiment exactly.** Its output for the 7 original profiles matched the saved experiment output line for line.
- **The modes really do rank differently.** `mood_first` is the only mode that puts Dusty Backroads (nostalgic country) above Night Drive Loop (synthwave) for Throwback Explorer. `genre_first` widens the gap between genre matches and everything else.
- **No mode fixes the Sad but Energetic profile.** Hollow Pines wins in all four, which shows the real problem there is the data (only one sad song), not the weights.
- **An invalid mode is rejected.** `--mode nope` was tested and prints an error listing the valid modes.
- *(Add your own checks here.)*

# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version, **TuneScout 1.0**, is a content-based recommender that suggests the top 5 songs from a 20-song catalog. Each song gets points for matching the listener's favourite genre and mood, and for being close to their target energy level (plus optional acoustic and positivity preferences). The songs are then ranked, and every recommendation lists the reasons behind its score. I stress-tested it with 7 user profiles, including 4 designed to trick it, and ran a weight-change experiment. What it gets right and wrong is documented below and in the [model card](model_card.md).

---

## How The System Works

Real-world platforms like Spotify and YouTube predict what you'll love by combining two approaches. **Collaborative filtering** learns from the behaviour of millions of users: plays, skips, saves, and playlist adds. **Content-based filtering** compares the attributes of the songs themselves, such as genre, mood, energy, and tempo. These signals feed a multi-stage pipeline: the system gathers candidate songs, scores each one for the user, and re-ranks the final list for variety and freshness. My simulation has no listening history from other users, so it is a **content-based recommender**. It prioritises matching a song's *vibe* to the user's stated taste. Genre carries the most weight, followed by mood and closeness to a target energy level, with acoustic preference as a smaller adjustment. Numeric features are scored by how *close* the song is to the user's preference, not by whether the value is high or low, so a user who wants calm music isn't automatically handed the most intense track.

**`Song` features used in scoring**
- `genre`: category (e.g. pop, lofi, rock), scored as an exact match
- `mood`: category (e.g. happy, chill, intense), scored as an exact match
- `energy`: 0–1, scored by closeness to the user's target
- `acousticness`: 0–1, rewarded high or low depending on the user's preference
- `valence`: 0–1 (musical positivity), optional, scored by closeness to the user's target
- *(Loaded but not scored yet: `tempo_bpm`, `danceability`. `title`, `artist`, and `id` are used for display and tie-breaking.)*

**`UserProfile` features**
- `favorite_genre`: the genre the user prefers
- `favorite_mood`: the mood the user is looking for
- `target_energy`: the ideal energy level, from 0 to 1
- `likes_acoustic`: whether the user prefers acoustic (`True`) or produced/electronic (`False`) sound
- `target_valence`: optional, the ideal positivity level, from 0 to 1

The command-line runner (`src/main.py`) passes the same preferences as a dictionary with the keys `genre`, `mood`, and `energy`, plus the optional `likes_acoustic` and `valence`.

### Algorithm Recipe

**1. Load:** read `data/songs.csv` (20 songs) and convert the numeric columns from text to numbers.

**2. Score each song (the scoring rule):** every song is judged on its own against the user's preferences:

| Feature | Points | How it's calculated |
|---|---|---|
| Genre | 2.0 | 2.0 if the song's genre matches the favourite genre, otherwise 0 |
| Mood | 1.5 | 1.5 if the song's mood matches the favourite mood, otherwise 0 |
| Energy | up to 1.5 | 1.5 × (1 − \|song energy − target energy\|) |
| Acousticness | up to 1.0 | 1.0 × acousticness if the user likes acoustic, otherwise 1.0 × (1 − acousticness) |
| Valence *(optional)* | up to 1.0 | 1.0 × (1 − \|song valence − target valence\|) |

```
score = 2.0·genre_match + 1.5·mood_match + 1.5·energy_closeness
      + 1.0·acoustic_fit + 1.0·valence_closeness
```

Terms for preferences the user didn't give are skipped. The maximum score is 7.5 with every preference set. Genre is the largest single weight, but it's smaller than mood + energy combined (3.0), so a song with the right vibe can still beat a song that only matches the genre. As the score is calculated, a short reason is recorded for each term (e.g. "genre matches pop", "energy 0.82 is close to your target 0.80") to build the explanation.

**3. Rank the list (the ranking rule):**
1. Sort all songs by score, highest first.
2. Break ties by closer energy, then by lower `id`, so results are always the same.
3. *(Not implemented yet)* Limit each artist to one song, for variety. See Future Work in the model card.
4. Return the top `k` songs, each with its score and explanation.

```
User prefs ──► score_song() for every song ──► sort + tie-break + diversity ──► top k
               (score + reasons)                                                (song, score, "because…")
```

### Expected Biases and Limitations

- **Genre over-prioritised:** genre is the largest weight, so a song in the user's genre with the wrong mood can outrank a great song in a neighbouring genre that matches the mood perfectly.
- **Exact-match categories:** `pop` and `indie pop`, or `chill` and `relaxed`, count as completely different, so closely related songs get no credit for their genre or mood.
- **Few songs per genre:** most genres have only one or two songs, so after the one exact match the list is filled mostly by energy and acousticness. These users effectively get a less personalised list than users of better-represented genres like lofi.
- **Correlated features:** energy, acousticness, and tempo tend to move together in this data, so "high-energy electronic" songs and "calm acoustic" songs get double-counted in their favour, and mixed songs (e.g. energetic acoustic folk) are hard to recommend.
- **One taste, fixed tolerance:** each user has a single favourite genre and mood, no dislikes, and the same tolerance for distance from their energy target, which doesn't reflect people with varied or very specific taste.
- **Hand-made data:** the song attributes were written by hand, not measured, so the recommendations reflect the assumptions built into the dataset.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default profile (`genre=pop, mood=happy, energy=0.8`). The full run, with all 7 profiles, is under [Experiments You Tried](#experiments-you-tried).

```
Loading songs from data/songs.csv...
Loaded songs: 20

High-Energy Pop: genre=pop, mood=happy, energy=0.8
============================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.97
   Why:
     - genre match: pop (+2.00)
     - mood match: happy (+1.50)
     - energy 0.82 vs target 0.80 (+1.47)

2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.30
   Why:
     - genre match: pop (+2.00)
     - energy 0.93 vs target 0.80 (+1.30)

3. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.94
   Why:
     - mood match: happy (+1.50)
     - energy 0.76 vs target 0.80 (+1.44)

4. Concrete Verses by Block Theory  [hip hop / confident]
   Score: 1.47
   Why:
     - energy 0.78 vs target 0.80 (+1.47)

5. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 1.42
   Why:
     - energy 0.75 vs target 0.80 (+1.42)
```

---

## Experiments You Tried

### Stress test: 7 user profiles

`src/main.py` runs every profile in `PROFILES` against all 20 songs. Three are normal listeners and four are adversarial, designed to try to trick the scoring logic.

| Profile | Preferences | What it tests |
|---|---|---|
| High-Energy Pop | pop, happy, energy 0.8 | The default, "easy" case |
| Chill Lofi | lofi, chill, energy 0.4, likes acoustic | Low energy; the genre with the most songs (3) |
| Deep Intense Rock | rock, intense, energy 0.9, non-acoustic | High energy; a genre with only 1 song |
| Sad but Energetic | folk, sad, energy 0.9 | Conflict: the only sad song is very low energy |
| Acoustic Metalhead | metal, angry, energy 0.95, likes acoustic | Conflict: metal songs are never acoustic |
| Capitalized Pop | Pop, Happy, energy 0.8 | Same as the default but with capital letters |
| Out-of-Range Energy | edm, euphoric, energy 1.5 | An energy target outside the 0–1 scale |

Full output of `python -m src.main`:

```
Loading songs from data/songs.csv...
Loaded songs: 20

High-Energy Pop: genre=pop, mood=happy, energy=0.8
============================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.97
   Why:
     - genre match: pop (+2.00)
     - mood match: happy (+1.50)
     - energy 0.82 vs target 0.80 (+1.47)

2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.30
   Why:
     - genre match: pop (+2.00)
     - energy 0.93 vs target 0.80 (+1.30)

3. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.94
   Why:
     - mood match: happy (+1.50)
     - energy 0.76 vs target 0.80 (+1.44)

4. Concrete Verses by Block Theory  [hip hop / confident]
   Score: 1.47
   Why:
     - energy 0.78 vs target 0.80 (+1.47)

5. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 1.42
   Why:
     - energy 0.75 vs target 0.80 (+1.42)


Chill Lofi: genre=lofi, mood=chill, energy=0.4, likes_acoustic=True
============================================================
1. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 5.79
   Why:
     - genre match: lofi (+2.00)
     - mood match: chill (+1.50)
     - energy 0.35 vs target 0.40 (+1.42)
     - acoustic fit, acousticness 0.86 (+0.86)

2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 5.68
   Why:
     - genre match: lofi (+2.00)
     - mood match: chill (+1.50)
     - energy 0.42 vs target 0.40 (+1.47)
     - acoustic fit, acousticness 0.71 (+0.71)

3. Focus Flow by LoRoom  [lofi / focused]
   Score: 4.28
   Why:
     - genre match: lofi (+2.00)
     - energy 0.40 vs target 0.40 (+1.50)
     - acoustic fit, acousticness 0.78 (+0.78)

4. Spacewalk Thoughts by Orbit Bloom  [ambient / chill]
   Score: 3.74
   Why:
     - mood match: chill (+1.50)
     - energy 0.28 vs target 0.40 (+1.32)
     - acoustic fit, acousticness 0.92 (+0.92)

5. Coffee Shop Stories by Slow Stereo  [jazz / relaxed]
   Score: 2.35
   Why:
     - energy 0.37 vs target 0.40 (+1.46)
     - acoustic fit, acousticness 0.89 (+0.89)


Deep Intense Rock: genre=rock, mood=intense, energy=0.9, likes_acoustic=False
============================================================
1. Storm Runner by Voltline  [rock / intense]
   Score: 5.88
   Why:
     - genre match: rock (+2.00)
     - mood match: intense (+1.50)
     - energy 0.91 vs target 0.90 (+1.48)
     - non-acoustic fit, acousticness 0.10 (+0.90)

2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.91
   Why:
     - mood match: intense (+1.50)
     - energy 0.93 vs target 0.90 (+1.46)
     - non-acoustic fit, acousticness 0.05 (+0.95)

3. Pulse Reactor by Kilowatt  [edm / euphoric]
   Score: 2.41
   Why:
     - energy 0.95 vs target 0.90 (+1.43)
     - non-acoustic fit, acousticness 0.02 (+0.98)

4. Iron Tempest by Graveforge  [metal / angry]
   Score: 2.37
   Why:
     - energy 0.97 vs target 0.90 (+1.40)
     - non-acoustic fit, acousticness 0.03 (+0.97)

5. Concrete Verses by Block Theory  [hip hop / confident]
   Score: 2.24
   Why:
     - energy 0.78 vs target 0.90 (+1.32)
     - non-acoustic fit, acousticness 0.08 (+0.92)


Sad but Energetic: genre=folk, mood=sad, energy=0.9
============================================================
1. Hollow Pines by Wren Hollow  [folk / sad]
   Score: 4.04
   Why:
     - genre match: folk (+2.00)
     - mood match: sad (+1.50)
     - energy 0.26 vs target 0.90 (+0.54)

2. Storm Runner by Voltline  [rock / intense]
   Score: 1.48
   Why:
     - energy 0.91 vs target 0.90 (+1.48)

3. Gym Hero by Max Pulse  [pop / intense]
   Score: 1.46
   Why:
     - energy 0.93 vs target 0.90 (+1.46)

4. Pulse Reactor by Kilowatt  [edm / euphoric]
   Score: 1.43
   Why:
     - energy 0.95 vs target 0.90 (+1.43)

5. Iron Tempest by Graveforge  [metal / angry]
   Score: 1.40
   Why:
     - energy 0.97 vs target 0.90 (+1.40)


Acoustic Metalhead: genre=metal, mood=angry, energy=0.95, likes_acoustic=True
============================================================
1. Iron Tempest by Graveforge  [metal / angry]
   Score: 5.00
   Why:
     - genre match: metal (+2.00)
     - mood match: angry (+1.50)
     - energy 0.97 vs target 0.95 (+1.47)
     - acoustic fit, acousticness 0.03 (+0.03)

2. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 1.56
   Why:
     - energy 0.76 vs target 0.95 (+1.22)
     - acoustic fit, acousticness 0.35 (+0.35)

3. Storm Runner by Voltline  [rock / intense]
   Score: 1.54
   Why:
     - energy 0.91 vs target 0.95 (+1.44)
     - acoustic fit, acousticness 0.10 (+0.10)

4. Dusty Backroads by Cedar & Pine  [country / nostalgic]
   Score: 1.54
   Why:
     - energy 0.55 vs target 0.95 (+0.90)
     - acoustic fit, acousticness 0.64 (+0.64)

5. Gym Hero by Max Pulse  [pop / intense]
   Score: 1.52
   Why:
     - energy 0.93 vs target 0.95 (+1.47)
     - acoustic fit, acousticness 0.05 (+0.05)


Capitalized Pop: genre=Pop, mood=Happy, energy=0.8
============================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 1.47
   Why:
     - energy 0.82 vs target 0.80 (+1.47)

2. Concrete Verses by Block Theory  [hip hop / confident]
   Score: 1.47
   Why:
     - energy 0.78 vs target 0.80 (+1.47)

3. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 1.44
   Why:
     - energy 0.76 vs target 0.80 (+1.44)

4. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 1.42
   Why:
     - energy 0.75 vs target 0.80 (+1.42)

5. Fuego Lento by Los Faroles  [latin / playful]
   Score: 1.38
   Why:
     - energy 0.72 vs target 0.80 (+1.38)


Out-of-Range Energy: genre=edm, mood=euphoric, energy=1.5
============================================================
1. Pulse Reactor by Kilowatt  [edm / euphoric]
   Score: 4.17
   Why:
     - genre match: edm (+2.00)
     - mood match: euphoric (+1.50)
     - energy 0.95 vs target 1.50 (+0.67)

2. Iron Tempest by Graveforge  [metal / angry]
   Score: 0.70
   Why:
     - energy 0.97 vs target 1.50 (+0.70)

3. Gym Hero by Max Pulse  [pop / intense]
   Score: 0.65
   Why:
     - energy 0.93 vs target 1.50 (+0.65)

4. Storm Runner by Voltline  [rock / intense]
   Score: 0.61
   Why:
     - energy 0.91 vs target 1.50 (+0.61)

5. Sunrise City by Neon Echo  [pop / happy]
   Score: 0.48
   Why:
     - energy 0.82 vs target 1.50 (+0.48)
```

**What stood out:**
- **The "Gym Hero effect":** Gym Hero (pop / intense, energy 0.93) appears in the top 5 for 5 of the 7 profiles, including rock, sad folk, and metal fans. Once the one or two genre/mood matches are used up, the rest of the list is decided almost entirely by energy, and Gym Hero is one of only four songs above 0.9.
- **Sad but Energetic:** Hollow Pines (folk / sad, energy 0.26) still wins, because matching genre and mood (+3.5) outweighs a terrible energy match. Every other pick is high-energy but none is sad. Iron Tempest (valence 0.24), arguably the best "sad and energetic" fit, comes 5th because valence wasn't part of this profile.
- **Acoustic Metalhead:** the contradiction pulls in odd songs. Rooftop Lights (indie pop / happy) and Dusty Backroads (country) reach the top 4 mostly on acoustic points.
- **Capitalized Pop:** "Pop" doesn't equal "pop", so genre and mood never match and the list is ranked by energy alone. Sunrise City still comes first, but only because it wins an exact tie with Concrete Verses on the tie-break (lower id).
- **Out-of-Range Energy:** the top 5 looks reasonable, but 8 low-energy songs get negative scores (down to −0.96). Energy 1.5 is accepted without any error.

### Experiment: weight shift (energy ×2, genre ×½)

I temporarily changed `GENRE_WEIGHT` from 2.0 to 1.0 and `ENERGY_WEIGHT` from 1.5 to 3.0, re-ran all profiles, then reverted. **Math check:** for any energy target between 0 and 1 the energy term stays between 0 and 3, so no score goes negative. The maximum score for a genre + mood + energy profile rises from 5.0 to 5.5, and since every song is scored the same way the ranking is still a fair comparison.

| Profile | Original top 5 (genre 2.0, energy 1.5) | Shifted top 5 (genre 1.0, energy 3.0) |
|---|---|---|
| High-Energy Pop | Sunrise City, **Gym Hero**, Rooftop Lights, Concrete Verses, Night Drive Loop | Sunrise City, **Rooftop Lights**, Gym Hero, Concrete Verses, Night Drive Loop |
| Chill Lofi | Library Rain, Midnight Coding, **Focus Flow**, Spacewalk Thoughts, Coffee Shop Stories | Library Rain, Midnight Coding, **Spacewalk Thoughts**, Focus Flow, Coffee Shop Stories |
| Deep Intense Rock | Storm Runner, Gym Hero, Pulse Reactor, Iron Tempest, **Concrete Verses** | Storm Runner, Gym Hero, Pulse Reactor, Iron Tempest, **Sunrise City** |
| Sad but Energetic | Hollow Pines, Storm Runner, Gym Hero, Pulse Reactor, Iron Tempest | *(same order)* Hollow Pines 3.58 vs Storm Runner 2.97 |
| Acoustic Metalhead | Iron Tempest, **Rooftop Lights**, Storm Runner, **Dusty Backroads**, Gym Hero | Iron Tempest, **Pulse Reactor**, Gym Hero, Storm Runner, **Sunrise City** |

**More accurate or just different? Mostly different, with a mixed result.**
- *Better:* Happy-pop fans now get the happy indie-pop song before the intense gym song, and chill fans get the chill ambient song before the "focused" lofi one. Matching the vibe beat matching the label.
- *Worse:* the rock fan now gets Sunrise City (happy pop) at #5, purely for its energy. With energy weighted this heavily, the high-energy bubble gets bigger.
- *Unchanged:* Hollow Pines still beats every energetic song for the Sad but Energetic profile, because genre + mood together (2.5) still outweigh a perfect energy match. For profiles ranked by energy alone (Capitalized Pop, Out-of-Range), the order stays the same and only the scores double.

I kept the original weights: the shift fixed some mood problems but made the energy bubble worse.

---

## Limitations and Risks

- **Tiny, made-up catalog:** 20 songs with hand-written values. Most genres have only one or two songs, so after the first match or two the lists fill up with "closest energy" picks.
- **High-energy filter bubble:** any high-energy listener gets the same few songs (Gym Hero appeared in 5 of my 7 test profiles), whatever genre or mood they asked for.
- **Strict matching:** "Pop" doesn't match "pop", and related labels like "chill" and "relaxed" get no partial credit.
- **No input checks:** an energy target of 1.5 is accepted and gives some songs negative scores.
- **Shallow understanding of music:** no lyrics, language, or listening history, so the system knows nothing about a song beyond its labels and numbers.

The model card covers these in more depth, under [Limitations and Bias](model_card.md#6-limitations-and-bias).

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this showed me that a recommender turns data into predictions by *scoring* and then *ranking*. Each song is reduced to a few labels and numbers, compared with what the listener asked for, and turned into a single score. The "prediction" is really just "the songs with the highest scores". It surprised me how much the results depend on choices that feel small: changing two weights reshuffled several lists, and how close a song's energy is to the target ended up deciding most of each top 5.

Bias shows up in places you wouldn't expect. Nothing in my code favours any particular song, yet Gym Hero kept appearing for rock, folk, and metal fans, simply because the catalog has very few songs per genre and only four very energetic ones. Users whose taste is under-represented in the data, like mid-energy listeners, or anyone who types "Pop" instead of "pop", quietly get worse recommendations. In a real app, the same thing could mean some artists and listeners are consistently overlooked without anyone deciding that on purpose.

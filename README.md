# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

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
3. Optionally allow at most one song per artist, for variety.
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

Output of `python -m src.main` for the default profile (`genre=pop, mood=happy, energy=0.8`):

```
Loading songs from data/songs.csv...
Loaded songs: 20

Top 5 recommendations for: genre=pop, mood=happy, energy=0.8
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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"


# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**TuneScout 1.0**

---

## 2. Intended Use  

**Goal / task:** TuneScout suggests the top 5 songs from a small catalog that best fit a listener's taste. It predicts which songs a person will like by comparing each song to the genre, mood, and energy level they ask for.

**Assumptions about the user:**
- They can name one favourite genre and one mood.
- They know roughly how energetic they want the music to be.
- Their taste doesn't change while they're listening.

**Intended use:** classroom learning. It's for exploring how recommenders turn data into suggestions, and for testing how small changes to the scoring rules change the results.

**Not intended for:**
- Real users or a real music app. The catalog is tiny and the song data is made up.
- Making decisions about artists, such as which songs get promoted or paid. The scores reflect hand-picked weights, not real listener behaviour.
- Judging what music is "good". A low score only means the song doesn't match one person's stated preferences.

---

## 3. How the Model Works  

TuneScout gives every song points, then shows the songs with the most points.

**How a song earns points:**
- **Right genre:** +2 points. This is the biggest single reward.
- **Right mood:** +1.5 points.
- **Close energy level:** up to +1.5 points. A song with exactly the energy you asked for gets all 1.5. The further away it is, the fewer points it gets. Being *close* is what counts, not being high or low.
- **Acoustic sound (optional):** up to +1 point. If you like acoustic music, more acoustic songs earn more. If you don't, less acoustic songs earn more.
- **Positivity, or "valence" (optional):** up to +1 point, for being close to how upbeat you want the music to feel.

**Picking the winners:** all the songs are sorted from most to fewest points. If two songs tie, the one with closer energy wins. The top 5 are shown, each with a list of the reasons it earned its points.

**Changes from the starter code:** the starter returned no recommendations. I added:
- the CSV loader
- the points system, which also lists its reasons
- the sorting and tie-breaking
- the readable terminal output
- a set of test profiles

I also fixed an import so `python -m src.main` works.

---

## 4. Data  

**Size:** 20 songs, stored in `data/songs.csv`. The starter had 10, and I added 10 more to cover genres and moods that were missing.

**Features for each song:**
- title and artist
- genre and mood
- energy, valence (positivity), danceability, and acousticness, each on a 0–1 scale
- tempo in beats per minute

**What's covered:**
- 17 genres, including pop, lofi, rock, jazz, hip hop, classical, metal, folk, latin, and blues
- 16 moods, including happy, chill, intense, sad, angry, and romantic

**Limits:**
- **The songs and their numbers are made up.** They were written by hand, not measured from real audio.
- **Most genres have only 1 or 2 songs.** Lofi has the most, with 3.
- **Energy is lopsided.** Only 3 songs sit in the middle of the energy range (0.45–0.7). Most are either quiet or very energetic.
- **Some taste is missing entirely.** There are no lyrics, language, decade, or popularity, and no listening history from real people.
- **The genre and mood labels reflect one point of view.** Someone else might tag the same song differently.

---

## 5. Strengths  

- **Clear, consistent tastes get great results.** Happy pop, chill lofi, and intense rock fans all got the song I'd have picked myself in first place.
- **It explains itself.** Every recommendation lists exactly where its points came from, so you can always see *why* a song was picked.
- **Opposite tastes get opposite lists.** The chill lofi and intense rock profiles share no songs at all. That shows the energy and acoustic scores really do separate different kinds of music.
- **It's predictable.** The same input always gives the same output, because ties are broken the same way every time.

---

## 6. Limitations and Bias 

**Main weakness: a high-energy "filter bubble".** Most genres in the catalog have only one or two songs, so after the first one or two genre/mood matches, the rest of every list is decided almost entirely by how close each song's energy is to the user's target. Because only four songs have energy above 0.9, any user who asks for high energy gets the same four songs (Storm Runner, Gym Hero, Pulse Reactor, Iron Tempest), whether they asked for rock, sad folk, metal, or EDM. Gym Hero showed up in the top 5 for 5 of my 7 test profiles. That means the system quietly ignores the rest of a high-energy user's taste and keeps recommending the same few tracks, and doubling the energy weight in my experiment made this bubble bigger, not smaller.

**Other weaknesses found while testing:**
- **Mid-energy listeners are underserved.** Only 3 of the 20 songs have energy between 0.45 and 0.7, so a user who wants something "in the middle" has very few close matches.
- **Exact text matching.** "Pop" and "pop" are treated as different genres, so a user who types capitals gets no genre or mood credit at all. Related labels like "chill" and "relaxed" also get no partial credit.
- **No input checks.** An energy target of 1.5 is accepted and gives low-energy songs negative scores instead of raising an error.
- **Conflicting preferences fall apart.** A user who likes acoustic metal gets indie pop and country in their top 5, because no song can satisfy both wishes and the leftover acoustic points decide the order.
- **Valence is ignored unless asked for.** A "sad but energetic" listener isn't shown Iron Tempest (very low valence, very high energy) near the top, because the default profile doesn't set a valence target.

---

## 7. Evaluation  

**Profiles tested.** I ran 7 profiles through `python -m src.main` and read the top 5 for each:
- Three normal listeners: **High-Energy Pop**, **Chill Lofi**, and **Deep Intense Rock**.
- Four "adversarial" profiles meant to trick the scoring:
  - **Sad but Energetic:** sad mood with high energy
  - **Acoustic Metalhead:** metal fan who likes acoustic sound
  - **Capitalized Pop:** "Pop" and "Happy" typed with capitals
  - **Out-of-Range Energy:** energy target of 1.5

The full terminal output is in the README under "Experiments You Tried". I also ran the two starter tests, and both pass.

**Does it feel right?** For the three normal listeners, yes. Sunrise City for happy pop, Library Rain and Midnight Coding for chill lofi, and Storm Runner for intense rock are exactly what I'd pick myself. The lists get less convincing after the first two songs, because the catalog runs out of songs in the right genre.

**Why did Storm Runner rank first for Deep Intense Rock?** It scored 5.88 out of a possible 6.0:
- +2.00 for matching rock
- +1.50 for matching intense
- +1.48 because its energy (0.91) is almost exactly the 0.9 target
- +0.90 because it's barely acoustic (0.10), which this user wanted

The runner-up, Gym Hero, only got 3.91, because it's pop rather than rock and loses the full 2 genre points.

**What surprised me:**
- How often Gym Hero turns up. It came up in 5 of the 7 lists.
- That Hollow Pines, a slow sad folk song, still wins for someone who wants *energetic* sad music. Matching the genre and the mood is worth more than matching the energy.
- That capital letters completely break the genre and mood matching.

**Why does "Gym Hero" keep showing up for people who just want "Happy Pop"?** The system gives points for three things: being the right genre, being the right mood, and having about the right energy level. Gym Hero is a pop song with very high energy (0.93, close to the 0.8 target), so it picks up the big genre bonus and nearly full energy points. It misses the "happy" bonus because it's tagged "intense", but that bonus (1.5 points) is smaller than the genre bonus (2 points). So the system decides "pop and energetic" beats "happy but not pop". A person would probably say a happy indie-pop song like Rooftop Lights fits better, and when I shrank the genre bonus in my experiment, Rooftop Lights did move above Gym Hero.

**Comparing profiles side by side.** With 7 profiles there are 21 possible pairs. Each one is compared below, grouped by the first profile in the pair.

*High-Energy Pop vs. the others*
- **High-Energy Pop vs. Chill Lofi:** The pop list is upbeat and electronic (energy around 0.75–0.93), while the lofi list shifts to quiet, acoustic songs (energy 0.28–0.42, acousticness 0.71–0.92). The two lists share no songs. That makes sense, because the profiles ask for opposite energy levels and only the lofi user rewards acoustic sound.
- **High-Energy Pop vs. Deep Intense Rock:** Both lists are high-energy and share Gym Hero, but the rock list is even more intense (energy 0.78–0.97) and swaps the happy songs for intense, angry, and euphoric ones. This makes sense: both users want energy, but the rock user's "intense" mood and non-acoustic preference push it toward harder songs like Iron Tempest.
- **High-Energy Pop vs. Sad but Energetic:** They share only Gym Hero. Both want high energy, but asking for "sad" puts a slow folk song (Hollow Pines) in first place, and the rest of the list turns intense rather than happy. That makes sense: mood is the main difference between them, and only one song in the catalog is tagged "sad".
- **High-Energy Pop vs. Capitalized Pop:** Same tastes, different capitalization, yet the capitalized list loses every genre and mood bonus and becomes a plain "closest energy" list. A latin song (Fuego Lento) moves in, and Gym Hero disappears. This doesn't make sense for a real user; it shows the matching is too strict.
- **High-Energy Pop vs. Acoustic Metalhead:** They share Rooftop Lights and Gym Hero, but for different reasons. The pop fan gets Rooftop Lights because it's happy. The metalhead gets it because it's slightly acoustic (0.35), the most acoustic song left at a decent energy level. The same song can be recommended for completely different reasons, which you can only tell from the "Why" lines.
- **High-Energy Pop vs. Out-of-Range Energy:** They share Gym Hero and Sunrise City, but Sunrise City falls from 1st to 5th. The out-of-range user asked for EDM and an energy above anything in the catalog, so the most extreme songs (0.91–0.97) move ahead of the "just right" 0.82 pop song. That makes sense, since 1.5 effectively means "as energetic as possible".

*Chill Lofi vs. the others*
- **Chill Lofi vs. Deep Intense Rock:** These are complete opposites, with no songs in common. Lofi gets slow, acoustic, low-energy tracks and rock gets fast, electronic, high-energy ones. This is the clearest sign the energy and acousticness scores are doing their job.
- **Chill Lofi vs. Sad but Energetic:** No songs in common. Interestingly, Hollow Pines (quiet, very acoustic) would suit the lofi listener's energy and acoustic taste, but it doesn't make their top 5 because there are enough chill songs that also match on genre or mood. It does top the sad listener's list despite its low energy. Either way, genre and mood labels decide who gets it.
- **Chill Lofi vs. Acoustic Metalhead:** Both say they like acoustic sound, yet the lofi list is very acoustic (0.71–0.92) and the metalhead list mostly isn't (0.03–0.64). In this catalog acoustic songs are always quiet, so the acoustic wish only works when it agrees with the energy wish, as it does for lofi.
- **Chill Lofi vs. Capitalized Pop:** No songs in common. With its labels broken, the capitalized profile is effectively "energy 0.8 please", so it gets mid-to-high energy songs (0.72–0.82), the opposite end of the scale from lofi.
- **Chill Lofi vs. Out-of-Range Energy:** No songs in common, and every one of the lofi listener's top 5 gets a *negative* score for the out-of-range profile (e.g. Library Rain −0.45). The two profiles sit at opposite ends of the energy scale, and the impossible 1.5 target pushes the quiet songs below zero.

*Deep Intense Rock vs. the others*
- **Deep Intense Rock vs. Sad but Energetic:** Positions 2–5 are almost the same four high-energy songs (Storm Runner, Gym Hero, Pulse Reactor, Iron Tempest), even though one user wants "intense" and the other wants "sad". When there's no mood match, energy takes over, which is the filter bubble described in Limitations.
- **Deep Intense Rock vs. Acoustic Metalhead:** The rock user's wishes all point the same way, so the list is clean and consistent. The metalhead's wishes contradict each other, so after Iron Tempest the list mixes indie pop, rock, country, and pop with scores all around 1.5. Close scores mean the system has no strong opinion, and the result looks random.
- **Deep Intense Rock vs. Capitalized Pop:** They share only Concrete Verses. The rock list sits at 0.78–0.97 energy and the capitalized list at 0.72–0.82. Both lists are largely ranked by energy closeness, so the difference is simply 0.9 vs. 0.8 as the target, which shows energy alone can shift a whole list.
- **Deep Intense Rock vs. Out-of-Range Energy:** Both lists are filled with the same high-energy songs, which makes sense because 1.5 just means "as energetic as possible". But the scores are much lower, and the quietest songs go negative, a sign the system should reject impossible inputs.

*Sad but Energetic vs. the others*
- **Sad but Energetic vs. Acoustic Metalhead:** These are the two "conflicting" profiles, and they share Storm Runner, Gym Hero, and Iron Tempest. Both are topped by the one song that matches their genre and mood, even though it fails their other wish (Hollow Pines isn't energetic; Iron Tempest isn't acoustic). That makes sense given the weights: labels are worth more than any single number.
- **Sad but Energetic vs. Capitalized Pop:** No songs in common. Both lists are ranked by energy once the labels stop matching, but toward different targets (0.9 vs. 0.8), so they land in neighbouring but separate clusters of songs.
- **Sad but Energetic vs. Out-of-Range Energy:** They share 4 of their 5 songs (Storm Runner, Gym Hero, Pulse Reactor, Iron Tempest), even though one asked for sad folk and the other for euphoric EDM. This is the clearest example of the high-energy filter bubble: the mood request barely matters once energy is high.

*Acoustic Metalhead vs. the others*
- **Acoustic Metalhead vs. Capitalized Pop:** They share only Rooftop Lights. The capitalized list is a smooth energy ranking, while the metalhead list jumps around (country, indie pop, rock) because the acoustic bonus keeps reshuffling songs with very close scores.
- **Acoustic Metalhead vs. Out-of-Range Energy:** They share Iron Tempest, Storm Runner, and Gym Hero. Without an acoustic wish, the out-of-range list is purely "loudest first". The metalhead's acoustic wish pulls in quieter songs like Dusty Backroads. Same high-energy core, with the acoustic preference as the only difference.

*Capitalized Pop vs. Out-of-Range Energy*
- **Capitalized Pop vs. Out-of-Range Energy:** They share only Sunrise City. Both lists depend mostly on energy, but the capitalized profile rewards songs *near* 0.8 while the 1.5 target is above every song, so "closest" turns into "highest is best". The same closeness formula produces two different behaviours depending on whether the target is inside the 0–1 range.

**Experiment.** I tried halving the genre weight (2.0 → 1.0) and doubling the energy weight (1.5 → 3.0). The results were mostly *different* rather than clearly better:
- Happy-pop and chill fans got better mood matches.
- The rock fan got a happy pop song in their top 5.

I went back to the original weights. Details are in the README.

---

## 8. Future Work  

1. **Make matching less strict.** Ignore capital letters, and give partial credit to related labels, such as "pop" and "indie pop", or "chill" and "relaxed".
2. **Add variety to the top 5.** Limit how often the same artist or the same handful of high-energy songs can appear, so lists like Gym Hero's don't keep repeating.
3. **Handle richer tastes.** Let users list more than one genre, say what they *don't* like, and reject impossible inputs like an energy of 1.5.

---

## 9. Personal Reflection  

**Biggest learning moment:** seeing the same song, Gym Hero, show up for a rock fan, a sad-folk fan, and a metal fan. Nothing in the code says "recommend Gym Hero". It happens because most genres only have one or two songs, so energy ends up deciding most of each list. That showed me a recommender's behaviour depends as much on the *data* as on the rules.

**How AI tools helped, and when I double-checked:** AI helped me research how Spotify and YouTube work, plan the scoring rule, write the code, and come up with tricky test profiles. But I had to check its work:
- Its first example claimed a chill lofi song would beat Gym Hero for a "pop but chill" listener. When we actually ran the numbers with all the preferences included, Gym Hero came out slightly ahead.
- During the weight experiment, the program kept running the experiment's weights even after the code was changed back. Python had kept an old compiled copy. We only caught it by comparing the output to the saved results.

The lesson: run it and check, don't just trust the explanation.

**What surprised me about simple algorithms:** a few lines of adding up points already *feels* like a real recommendation for normal listeners. The top picks matched my own instincts. It only feels "dumb" at the edges, like capital letters or contradictory tastes, which is a good reminder that real apps need far more testing than it seems.

**What I'd try next:** add simulated listening history, like plays and skips, so I could try collaborative filtering and combine it with my content-based scores into a hybrid recommender, like the real platforms use.  

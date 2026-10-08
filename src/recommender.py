import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k Song objects for the user, ranked by score_song."""
        songs_by_id = {song.id: song for song in self.songs}
        results = recommend_songs(_profile_to_prefs(user), [asdict(s) for s in self.songs], k)
        return [songs_by_id[song["id"]] for song, _, _ in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a readable string of the song's score and the reasons behind it."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)

def _profile_to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the user_prefs dict format used by score_song."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for key in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
                row[key] = float(row[key])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 1.5
ACOUSTIC_WEIGHT = 1.0
VALENCE_WEIGHT = 1.0

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against the user's preferences, returning (score, reasons)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.2f})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.2f})")

    # Numeric features reward closeness to the target, not higher or lower values
    if "energy" in user_prefs:
        points = ENERGY_WEIGHT * (1 - abs(song["energy"] - user_prefs["energy"]))
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{points:.2f})")

    if user_prefs.get("likes_acoustic") is not None:
        fit = song["acousticness"] if user_prefs["likes_acoustic"] else 1 - song["acousticness"]
        points = ACOUSTIC_WEIGHT * fit
        score += points
        label = "acoustic" if user_prefs["likes_acoustic"] else "non-acoustic"
        reasons.append(f"{label} fit, acousticness {song['acousticness']:.2f} (+{points:.2f})")

    if user_prefs.get("valence") is not None:
        points = VALENCE_WEIGHT * (1 - abs(song["valence"] - user_prefs["valence"]))
        score += points
        reasons.append(f"valence {song['valence']:.2f} vs target {user_prefs['valence']:.2f} (+{points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Ranking rule: highest score first; ties go to closer energy, then lower id
    target_energy = user_prefs.get("energy", 0.0)
    ranked = sorted(
        scored,
        key=lambda item: (-item[1], abs(item[0]["energy"] - target_energy), item[0]["id"]),
    )

    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]

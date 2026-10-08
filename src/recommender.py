import csv
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass, asdict, field

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
    # Advanced features (defaults keep older Song(...) calls working)
    popularity: int = 0
    release_decade: int = 0
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    language: str = ""

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
    target_valence: Optional[float] = None
    favorite_decade: Optional[int] = None
    mood_tags: Optional[List[str]] = None
    target_popularity: Optional[int] = None
    likes_instrumental: Optional[bool] = None
    language: Optional[str] = None

@dataclass(frozen=True)
class ScoringMode:
    """A scoring strategy: a named set of weights that score_song applies to each feature."""
    name: str
    description: str
    genre: float = 2.0
    mood: float = 1.5
    energy: float = 1.5
    acoustic: float = 1.0
    valence: float = 1.0
    decade: float = 1.0
    mood_tags: float = 1.0
    popularity: float = 0.5
    instrumental: float = 0.5
    language: float = 0.5

SCORING_MODES = {
    mode.name: mode
    for mode in [
        ScoringMode("balanced", "Default weights: genre first, then mood and energy"),
        ScoringMode("genre_first", "Genre dominates; mood and energy only order songs within a genre",
                    genre=4.0, mood=1.0, energy=1.0),
        ScoringMode("mood_first", "Mood and mood tags dominate; genre matters little",
                    genre=1.0, mood=3.0, mood_tags=2.0, valence=1.5),
        ScoringMode("energy_focused", "Energy closeness dominates; genre is halved",
                    genre=1.0, energy=3.0),
    ]
}
DEFAULT_MODE = "balanced"

def get_mode(mode: Union[str, ScoringMode, None]) -> ScoringMode:
    """Looks up a scoring mode by name, passing ScoringMode objects through unchanged."""
    if mode is None:
        return SCORING_MODES[DEFAULT_MODE]
    if isinstance(mode, ScoringMode):
        return mode
    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown scoring mode '{mode}'. Choose from: {', '.join(SCORING_MODES)}")
    return SCORING_MODES[mode]

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], mode: Union[str, ScoringMode] = DEFAULT_MODE):
        self.songs = songs
        self.mode = get_mode(mode)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k Song objects for the user, ranked by score_song."""
        songs_by_id = {song.id: song for song in self.songs}
        results = recommend_songs(_profile_to_prefs(user), [asdict(s) for s in self.songs], k, self.mode)
        return [songs_by_id[song["id"]] for song, _, _ in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a readable string of the song's score and the reasons behind it."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song), self.mode)
        return f"Score {score:.2f}: " + "; ".join(reasons)

def _profile_to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the user_prefs dict format used by score_song."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
        "valence": user.target_valence,
        "decade": user.favorite_decade,
        "mood_tags": user.mood_tags,
        "popularity": user.target_popularity,
        "likes_instrumental": user.likes_instrumental,
        "language": user.language,
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
            for key in ("energy", "tempo_bpm", "valence", "danceability", "acousticness", "instrumentalness"):
                row[key] = float(row[key])
            row["popularity"] = int(row["popularity"])
            row["release_decade"] = int(row["release_decade"])
            row["mood_tags"] = row["mood_tags"].split("|") if row["mood_tags"] else []
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict, mode: Union[str, ScoringMode, None] = None) -> Tuple[float, List[str]]:
    """Scores one song against the user's preferences, returning (score, reasons)."""
    weights = get_mode(mode)
    score = 0.0
    reasons = []

    def add(points: float, reason: str) -> None:
        nonlocal score
        score += points
        reasons.append(f"{reason} (+{points:.2f})")

    if song["genre"] == user_prefs.get("genre"):
        add(weights.genre, f"genre match: {song['genre']}")

    if song["mood"] == user_prefs.get("mood"):
        add(weights.mood, f"mood match: {song['mood']}")

    # Numeric features reward closeness to the target, not higher or lower values
    if "energy" in user_prefs:
        points = weights.energy * (1 - abs(song["energy"] - user_prefs["energy"]))
        add(points, f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f}")

    if user_prefs.get("likes_acoustic") is not None:
        fit = song["acousticness"] if user_prefs["likes_acoustic"] else 1 - song["acousticness"]
        label = "acoustic" if user_prefs["likes_acoustic"] else "non-acoustic"
        add(weights.acoustic * fit, f"{label} fit, acousticness {song['acousticness']:.2f}")

    if user_prefs.get("valence") is not None:
        points = weights.valence * (1 - abs(song["valence"] - user_prefs["valence"]))
        add(points, f"valence {song['valence']:.2f} vs target {user_prefs['valence']:.2f}")

    # Advanced features: each is skipped unless the user sets a preference for it
    if user_prefs.get("decade") is not None:
        gap = abs(song.get("release_decade", 0) - user_prefs["decade"])
        if gap == 0:
            add(weights.decade, f"from the {user_prefs['decade']}s")
        elif gap == 10:
            add(weights.decade * 0.5, f"{song['release_decade']}s is next to the {user_prefs['decade']}s")

    if user_prefs.get("mood_tags"):
        shared = [tag for tag in user_prefs["mood_tags"] if tag in song.get("mood_tags", [])]
        if shared:
            # Full points for 2+ shared tags, half for 1
            add(weights.mood_tags * min(len(shared), 2) / 2, f"mood tags: {', '.join(shared)}")

    if user_prefs.get("popularity") is not None:
        points = weights.popularity * (1 - abs(song.get("popularity", 0) - user_prefs["popularity"]) / 100)
        add(points, f"popularity {song.get('popularity', 0)} vs target {user_prefs['popularity']}")

    if user_prefs.get("likes_instrumental") is not None:
        instrumentalness = song.get("instrumentalness", 0.0)
        fit = instrumentalness if user_prefs["likes_instrumental"] else 1 - instrumentalness
        label = "instrumental" if user_prefs["likes_instrumental"] else "vocal"
        add(weights.instrumental * fit, f"{label} fit, instrumentalness {instrumentalness:.2f}")

    if user_prefs.get("language") and song.get("language") == user_prefs["language"]:
        add(weights.language, f"language: {song['language']}")

    return score, reasons

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, mode: Union[str, ScoringMode, None] = None
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    weights = get_mode(mode)
    scored = [(song, *score_song(user_prefs, song, weights)) for song in songs]

    # Ranking rule: highest score first; ties go to closer energy, then lower id
    target_energy = user_prefs.get("energy", 0.0)
    ranked = sorted(
        scored,
        key=lambda item: (-item[1], abs(item[0]["energy"] - target_energy), item[0]["id"]),
    )

    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]

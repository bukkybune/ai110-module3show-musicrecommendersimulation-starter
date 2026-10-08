"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse

from src.recommender import DEFAULT_MODE, SCORING_MODES, load_songs, recommend_songs


PROFILES = {
    # Starter example profile
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},

    # Adversarial / edge-case profiles that try to trick the scoring logic
    "Sad but Energetic": {"genre": "folk", "mood": "sad", "energy": 0.9},
    "Acoustic Metalhead": {"genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": True},
    "Capitalized Pop": {"genre": "Pop", "mood": "Happy", "energy": 0.8},
    "Out-of-Range Energy": {"genre": "edm", "mood": "euphoric", "energy": 1.5},

    # Uses the advanced features (decade, mood tags, popularity, instrumentalness)
    "Throwback Explorer": {
        "genre": "synthwave", "mood": "nostalgic", "energy": 0.6, "decade": 1980,
        "mood_tags": ["nostalgic", "dreamy"], "popularity": 50, "likes_instrumental": True,
    },
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    prefs_text = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print(f"\n{name}: {prefs_text}")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f}")
        print("   Why:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=SCORING_MODES, default=DEFAULT_MODE,
                        help="scoring strategy to rank songs with (default: %(default)s)")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    mode = SCORING_MODES[args.mode]
    print(f"Scoring mode: {mode.name} ({mode.description})")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()

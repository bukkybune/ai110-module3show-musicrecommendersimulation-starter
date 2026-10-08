"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


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
    songs = load_songs("data/songs.csv")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()

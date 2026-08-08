import csv
import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "German_A1_800_with_IPA.csv"
PROGRESS_FILE = BASE_DIR / "german_a1_progress.json"


def load_vocabulary():
    if not CSV_FILE.exists():
        print(f"\nERROR: I cannot find:\n{CSV_FILE}")
        print("\nPut German_A1_800_with_IPA.csv in the SAME folder as this Python file.")
        input("\nPress Enter to close...")
        raise SystemExit

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    vocabulary = []
    for i, row in enumerate(rows):
        german = (row.get("German") or "").strip()
        ipa = (row.get("IPA") or "").strip()
        english = (row.get("English") or "").strip()
        topic = (row.get("Topic") or "Unknown").strip()

        if german and english:
            vocabulary.append({
                "id": str(i),
                "german": german,
                "ipa": ipa,
                "english": english,
                "topic": topic
            })

    return vocabulary


def load_progress():
    if not PROGRESS_FILE.exists():
        return {}

    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def ensure_card(progress, card_id):
    if card_id not in progress:
        progress[card_id] = {
            "correct": 0,
            "wrong": 0,
            "streak": 0,
            "mastered": False
        }


def update_progress(progress, card_id, correct):
    ensure_card(progress, card_id)
    card = progress[card_id]

    if correct:
        card["correct"] += 1
        card["streak"] += 1
        if card["streak"] >= 3:
            card["mastered"] = True
    else:
        card["wrong"] += 1
        card["streak"] = 0
        card["mastered"] = False

    save_progress(progress)


def normalize(text):
    text = text.lower().strip()
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss"
    }
    for a, b in replacements.items():
        text = text.replace(a, b)

    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def answer_matches(user_answer, expected):
    user = normalize(user_answer)
    expected_norm = normalize(expected)

    if user == expected_norm:
        return True

    alternatives = []
    for part in expected.replace(";", "/").replace(",", "/").split("/"):
        part = normalize(part)
        if part:
            alternatives.append(part)

    return user in alternatives


def clear():
    print("\n" * 3)


def pause():
    input("\nPress Enter to continue...")


def topics_from(vocabulary):
    return sorted(set(v["topic"] for v in vocabulary))


def show_stats(vocabulary, progress):
    total = len(vocabulary)
    studied = sum(1 for v in vocabulary if v["id"] in progress)
    mastered = sum(
        1 for v in vocabulary
        if progress.get(v["id"], {}).get("mastered", False)
    )

    correct = sum(x.get("correct", 0) for x in progress.values())
    wrong = sum(x.get("wrong", 0) for x in progress.values())
    attempts = correct + wrong
    accuracy = (correct / attempts * 100) if attempts else 0

    print("\n==============================")
    print("YOUR GERMAN A1 PROGRESS")
    print("==============================")
    print(f"Vocabulary:     {total}")
    print(f"Studied:        {studied}")
    print(f"Mastered:       {mastered}")
    print(f"Correct:        {correct}")
    print(f"Wrong:          {wrong}")
    print(f"Accuracy:       {accuracy:.1f}%")
    print("==============================")


def choose_topic(vocabulary):
    topics = topics_from(vocabulary)

    print("\nChoose a topic:")
    print("0. All topics")

    for i, topic in enumerate(topics, start=1):
        count = sum(1 for v in vocabulary if v["topic"] == topic)
        print(f"{i}. {topic} ({count} words)")

    while True:
        choice = input("\nTopic number: ").strip()

        if choice == "0":
            return vocabulary

        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(topics):
                chosen = topics[n - 1]
                return [v for v in vocabulary if v["topic"] == chosen]

        print("Please enter a valid topic number.")


def get_cards(vocabulary, progress, mistakes_only=False):
    cards = vocabulary[:]

    if mistakes_only:
        cards = [
            v for v in cards
            if progress.get(v["id"], {}).get("wrong", 0) > 0
            and not progress.get(v["id"], {}).get("mastered", False)
        ]

    def priority(card):
        p = progress.get(card["id"], {})
        wrong = p.get("wrong", 0)
        correct = p.get("correct", 0)
        mastered = p.get("mastered", False)

        if mastered:
            return 3
        if wrong > 0:
            return 0
        if correct == 0:
            return 1
        return 2

    random.shuffle(cards)
    cards.sort(key=priority)
    return cards


def quiz(vocabulary, progress, direction="de_en", mistakes_only=False):
    cards = get_cards(vocabulary, progress, mistakes_only)

    if not cards:
        print("\nNo cards available for this mode.")
        pause()
        return

    try:
        amount = int(input(f"\nHow many cards? (1-{len(cards)}): ").strip())
    except ValueError:
        amount = min(20, len(cards))

    amount = max(1, min(amount, len(cards)))
    selected = cards[:amount]
    score = 0

    for number, card in enumerate(selected, start=1):
        clear()

        print("========================================")
        print(f"GERMAN A1     Card {number}/{amount}")
        print(f"Topic: {card['topic']}")
        print("========================================")

        if direction == "de_en":
            print(f"\nGERMAN:\n\n{card['german']}")
            print(f"{card['ipa']}\n")
            expected = card["english"]
            answer = input("English: ").strip()
        else:
            print(f"\nENGLISH:\n\n{card['english']}\n")
            expected = card["german"]
            answer = input("German: ").strip()

        if answer == "":
            print(f"\nAnswer: {expected}")
            if direction == "en_de":
                print(f"IPA: {card['ipa']}")
            result = input("\nDid you know it? (y/n): ").strip().lower()
            correct = result == "y"
        else:
            correct = answer_matches(answer, expected)
            print(f"\nCorrect answer: {expected}")
            print(f"IPA: {card['ipa']}")

        if correct:
            print("\n✓ CORRECT")
            score += 1
        else:
            print("\n✗ REVIEW THIS WORD")

        update_progress(progress, card["id"], correct)

        p = progress[card["id"]]
        print(
            f"\nCard progress: "
            f"{p['correct']} correct | "
            f"{p['wrong']} wrong | "
            f"streak {p['streak']}/3"
        )

        if p["mastered"]:
            print("★ MASTERED")

        input("\nPress Enter for the next card...")

    clear()
    percentage = score / amount * 100

    print("==============================")
    print("SESSION COMPLETE")
    print("==============================")
    print(f"Score: {score}/{amount}")
    print(f"Accuracy: {percentage:.1f}%")
    print("==============================")
    pause()


def flashcard_mode(vocabulary):
    cards = vocabulary[:]
    random.shuffle(cards)

    try:
        amount = int(input(f"\nHow many cards? (1-{len(cards)}): "))
    except ValueError:
        amount = min(20, len(cards))

    amount = max(1, min(amount, len(cards)))

    for i, card in enumerate(cards[:amount], start=1):
        clear()
        print("========================================")
        print(f"FLASHCARD {i}/{amount}")
        print(f"Topic: {card['topic']}")
        print("========================================")
        print(f"\nGERMAN:\n\n{card['german']}")
        print(f"\nIPA:\n{card['ipa']}")

        input("\nPress Enter to reveal...")

        print(f"\nENGLISH:\n\n{card['english']}")
        input("\nPress Enter for the next card...")


def main():
    vocabulary = load_vocabulary()
    progress = load_progress()

    while True:
        clear()
        print("==========================================")
        print("       GERMAN A1 FLASHCARD TRAINER")
        print("==========================================")
        print(f"Vocabulary loaded: {len(vocabulary)} words")
        print()
        print("1. German -> English quiz")
        print("2. English -> German quiz")
        print("3. Flashcard study mode")
        print("4. Review my mistakes")
        print("5. Study a specific topic")
        print("6. View progress")
        print("7. Reset progress")
        print("0. Exit")
        print("==========================================")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            quiz(vocabulary, progress, direction="de_en")
        elif choice == "2":
            quiz(vocabulary, progress, direction="en_de")
        elif choice == "3":
            flashcard_mode(vocabulary)
        elif choice == "4":
            print("\nMistakes review:")
            print("1. German -> English")
            print("2. English -> German")
            sub = input("Choose: ").strip()

            if sub == "2":
                quiz(vocabulary, progress, "en_de", mistakes_only=True)
            else:
                quiz(vocabulary, progress, "de_en", mistakes_only=True)
        elif choice == "5":
            selected = choose_topic(vocabulary)
            print("\n1. German -> English")
            print("2. English -> German")
            print("3. Flashcards")
            sub = input("Choose: ").strip()

            if sub == "2":
                quiz(selected, progress, "en_de")
            elif sub == "3":
                flashcard_mode(selected)
            else:
                quiz(selected, progress, "de_en")
        elif choice == "6":
            show_stats(vocabulary, progress)
            pause()
        elif choice == "7":
            confirm = input(
                "\nThis will delete all saved progress. Type RESET: "
            ).strip()

            if confirm == "RESET":
                progress = {}
                save_progress(progress)
                print("\nProgress reset.")
                pause()
        elif choice == "0":
            print("\nBis bald! Keep studying German.")
            break
        else:
            print("\nInvalid option.")
            pause()


if __name__ == "__main__":
    main()

"""
Translate natural language questions from English to Indonesian using Google Translate.

This module handles Phase 1 of the pipeline: translating the `question` field
in dev.json, train_spider.json, and train_others.json.

SQL queries, identifiers, and AST structures are NOT modified here;
those are handled by apply_translation.py using the schema dict.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from tqdm import tqdm


class QuestionTranslator:
    """Translates NL questions using googletrans with rate limiting and resume support."""

    def __init__(self, delay: float = 0.3, batch_pause: float = 2.0, batch_size: int = 10):
        import asyncio
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass
        from googletrans import Translator
        self.translator = Translator()
        self.delay = delay
        self.batch_pause = batch_pause
        self.batch_size = batch_size
        self._call_count = 0
        try:
            self._loop = asyncio.get_event_loop()
            if self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

    def _run_translate(self, text: str):
        """Run the async translate call synchronously."""
        import asyncio
        coro = self.translator.translate(text, src="en", dest="id")
        if asyncio.iscoroutine(coro):
            return self._loop.run_until_complete(coro)
        return coro

    def translate_text(self, text: str) -> str:
        """Translate a single text string from English to Indonesian."""
        self._call_count += 1
        try:
            result = self._run_translate(text)
            translated = result.text if hasattr(result, "text") else str(result)
            return translated.strip()
        except TypeError:
            try:
                result = self._run_translate(text)
                if isinstance(result, list):
                    return result[0].text.strip()
                return result.text.strip()
            except Exception:
                return text
        except Exception:
            return text
        finally:
            # Rate limiting
            if self._call_count % self.batch_size == 0:
                time.sleep(self.batch_pause)
            else:
                time.sleep(self.delay)


def translate_questions_file(
    input_path: Path,
    output_path: Path,
    translator: QuestionTranslator,
    save_every: int = 50,
) -> list[dict]:
    """Translate questions in a Spider JSON file.

    For each entry:
    - `question` → translated to Indonesian
    - `question_en` → original English question (preserved)
    - All other fields remain unchanged (will be modified by apply_translation later)

    Supports resume: if output_path exists with partial results, continues from
    the last translated entry.
    """
    with open(input_path, encoding="utf-8") as f:
        entries = json.load(f)

    # Resume support
    start_idx = 0
    if output_path.exists():
        try:
            with open(output_path, encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, list) and len(existing) > 0:
                start_idx = len(existing)
                print(f"  Resuming from entry {start_idx}/{len(entries)}")
                # Merge: keep existing translations, will translate remainder
                for i in range(min(start_idx, len(entries))):
                    if i < len(existing):
                        entries[i]["question_id"] = existing[i].get("question_id", entries[i]["question"])
                        entries[i]["question_en"] = existing[i].get("question_en", entries[i]["question"])
        except (json.JSONDecodeError, KeyError):
            start_idx = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    for i in tqdm(range(start_idx, len(entries)), desc=f"Translating {input_path.name}"):
        entry = entries[i]
        original_question = entry["question"]

        # Translate the question
        translated = translator.translate_text(original_question)

        entry["question_en"] = original_question
        entry["question_id"] = translated

        # Periodic save
        if (i + 1) % save_every == 0:
            _save_partial(entries, i + 1, output_path)

    # Final save
    _save_partial(entries, len(entries), output_path)
    return entries


def _save_partial(entries: list[dict], count: int, output_path: Path):
    """Save partially translated entries to disk."""
    to_save = entries[:count]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)


def run_phase1(
    spider_dir: Path,
    output_dir: Path,
    delay: float = 0.3,
    batch_pause: float = 2.0,
):
    """Run Phase 1: translate all questions.

    Translates questions in dev.json, train_spider.json, train_others.json,
    and test_data/dev.json if it exists.

    Results saved to output_dir/translated_questions/.
    """
    print("=" * 60)
    print("Phase 1: Translating Questions")
    print("=" * 60)

    translator = QuestionTranslator(delay=delay, batch_pause=batch_pause)
    output_dir.mkdir(parents=True, exist_ok=True)

    files_to_translate = [
        ("dev.json", spider_dir / "dev.json"),
        ("train_spider.json", spider_dir / "train_spider.json"),
        ("train_others.json", spider_dir / "train_others.json"),
    ]

    # Also translate test questions if available
    test_dev = spider_dir / "test_data" / "dev.json"
    if test_dev.exists():
        files_to_translate.append(("test_dev.json", test_dev))

    for out_name, in_path in files_to_translate:
        if not in_path.exists():
            print(f"\n  Skipping {in_path} (not found)")
            continue

        out_path = output_dir / out_name
        print(f"\n  Translating {in_path.name}...")

        with open(in_path, encoding="utf-8") as f:
            count = len(json.load(f))
        print(f"  {count} entries to translate")

        translate_questions_file(in_path, out_path, translator)
        print(f"  Saved to {out_path}")

    print("\nPhase 1 complete.")

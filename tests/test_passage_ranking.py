import unittest
from dataclasses import FrozenInstanceError

from src.ragforge.services.passage_ranking import Passage, ScopedPassageIndex


def ids(hits):
    return [hit.passage.passage_id for hit in hits]


class PassageRankingTests(unittest.TestCase):
    def test_french_accents_apostrophes_and_lexical_no_match(self):
        index = ScopedPassageIndex([
            Passage("one", "a", "Les frais d’hébergement"),
            Passage("two", "b", "Horaires de bureau"),
        ])
        self.assertEqual(ids(index.lexical("HEBERGEMENT")), ["one"])
        self.assertEqual(index.lexical("trésorerie"), ())

    def test_arabic_vowels_alef_digits_and_original_text(self):
        original = "إِجْرَاء ٢٧"
        index = ScopedPassageIndex([Passage("ar", "a", original)])
        for query in ("اجراء", "27"):
            with self.subTest(query=query):
                hit, = index.lexical(query)
                self.assertEqual(hit.passage.text, original)
                self.assertEqual(hit.lexical_rank, 1)
                self.assertIsNone(hit.dense_rank)

    def test_exact_reference_is_ranked_before_separate_parts(self):
        index = ScopedPassageIndex([
            Passage("split", "one", "REF RH 07"),
            Passage("exact", "two", "Réf‑RH‑07"),
        ])
        self.assertEqual(ids(index.lexical("REF-RH-07")), ["exact", "split"])

    def test_full_lexical_corpus_contributes_even_when_dense_misses_it(self):
        index = ScopedPassageIndex([
            Passage("from-words", "a", "RH-72"),
            Passage("from-vector", "b", "conditions de remboursement"),
        ])
        hits = index.hybrid("RH-72", ["from-vector"])
        self.assertEqual(set(ids(hits)), {"from-words", "from-vector"})
        self.assertEqual([(h.lexical_rank, h.dense_rank) for h in hits], [(None, 1), (1, None)])

    def test_fusion_formula_duplicate_and_foreign_ids(self):
        index = ScopedPassageIndex([
            Passage("a", "one", "budget"),
            Passage("b", "two", "budget"),
            Passage("c", "three", "dépenses"),
        ])
        hits = index.hybrid("budget", ["missing", "b", "b", "c"], rank_constant=10)
        self.assertEqual(ids(hits), ["b", "a", "c"])
        self.assertEqual((hits[0].lexical_rank, hits[0].dense_rank), (2, 1))
        self.assertAlmostEqual(hits[0].score, 1 / 12 + 1 / 11)
        self.assertAlmostEqual(hits[2].score, 1 / 12)

    def test_candidate_depth_and_result_limit_are_independent(self):
        index = ScopedPassageIndex([
            Passage("a", "a", "tarif"),
            Passage("b", "b", "tarif"),
            Passage("c", "c", "autre"),
        ])
        self.assertEqual(ids(index.hybrid("tarif", ["x", "c", "b"], candidate_limit=1)), ["a", "c"])
        self.assertEqual(ids(index.hybrid("tarif", ["b"], limit=1)), ["b"])

    def test_blank_query_empty_corpus_and_blank_document(self):
        index = ScopedPassageIndex([Passage("empty", "a", "")])
        self.assertEqual(index.hybrid(" ? ", ["empty"]), ())
        self.assertEqual(index.lexical("texte"), ())
        self.assertEqual(ScopedPassageIndex([]).hybrid("texte", ["missing"]), ())

    def test_equal_scores_are_independent_of_index_construction_order(self):
        passages = [Passage("a", "x", "tarif"), Passage("b", "y", "tarif")]
        for corpus in (passages, reversed(passages)):
            index = ScopedPassageIndex(corpus)
            self.assertEqual(ids(index.lexical("tarif")), ["a", "b"])
            self.assertEqual(ids(index.hybrid("tarif", [])), ["a", "b"])

    def test_invalid_ids_parameters_and_immutable_passage(self):
        passage = Passage("a", "doc", "texte")
        with self.assertRaises(FrozenInstanceError):
            passage.text = "changed"
        for corpus in ([passage, passage], [Passage("", "doc", "x")], [Passage("a", " ", "x")]):
            with self.subTest(corpus=corpus), self.assertRaises(ValueError):
                ScopedPassageIndex(corpus)
        index = ScopedPassageIndex([passage])
        for kwargs in ({"limit": 0}, {"rank_constant": False}, {"candidate_limit": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                index.hybrid("query", [], **kwargs)


if __name__ == "__main__":
    unittest.main()

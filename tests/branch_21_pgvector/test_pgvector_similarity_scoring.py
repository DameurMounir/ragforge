from src.ragforge.providers.vector_db.enums import DistanceMethod


def test_cosine_distance_is_converted_to_similarity_score(make_pgvector_provider):
    provider = make_pgvector_provider(distance=DistanceMethod.COSINE.value)
    assert provider._score_from_distance(0.0) == 1.0
    assert provider._score_from_distance(0.25) == 0.75


def test_dot_distance_is_converted_back_to_inner_product_score(
    make_pgvector_provider,
):
    provider = make_pgvector_provider(distance=DistanceMethod.DOT.value)
    assert provider._score_from_distance(-0.7) == 0.7


def test_euclidean_distance_is_converted_to_monotonic_similarity_score(
    make_pgvector_provider,
):
    provider = make_pgvector_provider(distance=DistanceMethod.EUCLID.value)
    assert provider._score_from_distance(0.0) == 1.0
    assert provider._score_from_distance(1.0) == 0.5


def test_vector_literal_rejects_wrong_dimension_early(make_pgvector_provider):
    provider = make_pgvector_provider(vector_size=4)
    try:
        provider._vector_to_pg_literal([0.1, 0.2, 0.3])
    except Exception as error:
        assert 'configured for vectors of size 4' in str(error)
    else:
        raise AssertionError('Expected wrong vector dimension to fail')


def test_vector_literal_serializes_to_pgvector_text_format(make_pgvector_provider):
    provider = make_pgvector_provider(vector_size=3)
    assert provider._vector_to_pg_literal([0.1, 0.2, 0.3]) == '[0.1,0.2,0.3]'

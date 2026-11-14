from stream.routing import topic_matches


def test_topic_routing():
    assert topic_matches("bangalore.koramangala.*", "bangalore.koramangala.food")
    assert topic_matches("bangalore.*.ride", "bangalore.whitefield.ride")
    assert topic_matches("bangalore.#", "bangalore.koramangala")
    assert not topic_matches("chennai.tnagar.food", "chennai.whitefield.food")
    assert not topic_matches("bangalore.*.ride", "bangalore.ride")

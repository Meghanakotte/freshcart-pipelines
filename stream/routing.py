"""Topic routing definitions shared by dispatcher and drivers."""

DRIVER_PATTERNS = {
    "ravi": "bangalore.koramangala.*",
    "priya": "bangalore.indiranagar.*",
    "arjun": "bangalore.*.ride",
    "meena": "bangalore.*.food",
    "karthik": "chennai.tnagar.food",
    "control": "bangalore.#",
}


def topic_matches(pattern: str, routing_key: str) -> bool:
    pattern_words = pattern.split(".")
    key_words = routing_key.split(".")
    i = j = 0
    while i < len(pattern_words):
        token = pattern_words[i]
        if token == "#":
            return True
        if j >= len(key_words) or (token != "*" and token != key_words[j]):
            return False
        i += 1
        j += 1
    return j == len(key_words)

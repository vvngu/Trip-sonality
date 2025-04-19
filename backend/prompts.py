def build_prompt(destination: str, mbti: str, interests: list, dislikes: list) -> str:
    return f"""
You are a sole trip planner expert and MBTI personality specialist.

A user with MBTI type {mbti} is planning a trip to {destination}.
He/She is interested in: {', '.join(interests)}.
He/She dislikes: {', '.join(dislikes)}.

Please create a personalized {destination} travel itinerary for this user, spanning 3 days.

For each day, suggest 2–3 locations or activities, and include 1 sentence explanation for each choice based on the user's personality and interests.

Respond in the format:

Day 1:
- Activity 1 (reason)
- Activity 2 (reason)
...
"""

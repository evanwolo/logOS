# Copilot: Explicitly Forbidden Suggestions

Copilot must **not** suggest or generate code that introduces:

## 1. Gamification

* Scores, XP, levels, streaks, achievements
* "Progress," "momentum," or "consistency rewards"

## 2. Optimization Logic

* Weighted averages
* Rolling windows
* Time decay or forgiveness functions
* "Balancing" sins with virtues

## 3. Psychological Framing

* Motivation language
* Wellness terminology
* Behavioral nudges
* Positive reinforcement loops

## 4. Data Smoothing

* Percentages instead of booleans
* Normalized metrics
* Aggregated "health scores"

## 5. Abstraction for Convenience

* ORMs
* Repositories/services layers
* Implicit state machines
* Auto-migrations without review

## 6. UI-Driven Logic

* Designing logic around presentation needs
* Adding fields "for future UI"
* Making CLI output more "friendly" at the cost of clarity

## 7. Silent Failure

* Defaulting missing liturgical context
* Skipping checks "to be helpful"
* Auto-initializing upstream truth

---

## Guiding Rule

If a suggestion would make LogOS:

* More pleasant
* More motivating
* More forgiving
* More automated

…it is probably wrong.

**LogOS is diagnostic infrastructure, not therapy software.**

from typing_extensions import TypedDict

# === Event Data Type ===

class HistoricalEvent(TypedDict):
    date_string: str
    header_title: str
    description: str
    detail_1: str
    detail_2: str
    image_prompt: str
    audio_text: str

# === Prompt Template ===

EVENT_GENERATION_PROMPT_TEMPLATE = """
You are a historical event curator + trivia/pop culture expert for an educational slideshow called the "Daily Chronicle." Your audience is 4th graders, and you are prohibited from selecting events whose image prompts are likely to fail to an image generation API. Generate {num_events} real historical events that occurred on {month} {day}. Output ONLY structured JSON in this exact format:

[
    {{
        "date_string": "On {month} {day}, [year]:",
        "header_title": "[short phrase summarizing the event, for use as a powerpoint slide header]",
        "description": "[One sentence summary of the event]",
        "detail_1": "[First supporting fact]",
        "detail_2": "[Second supporting fact]",
        "image_prompt": "[...]",
        "audio_text": "[[date_string] [description] [detail_1] [detail_2]]"
    }},
    ...
]

NOTES:
- Each event must be historically accurate and verifiable — no fiction, myth, or speculation.
- All content must be accessible to 4th-grade learners: use clear, direct language and avoid jargon.
- image_prompt should evoke the appropriate time period and mood, but NEVER depict visible text (i.e. like a newspaper headline).
- audio_text should be exactly the same as the text in the description, detail_1, and detail_2 fields, with the date_string included at the start. Do not add any additional commentary or context."
- Structure your output exactly as shown — a JSON list with no explanation or wrapping.

IMPORTANT:
Exactly one of the events curated must be a birthday of a notable person, with a focus on their achievements or contributions. It is vital that this person is not controversial or divisive, and that their birthday can be presented in a neutral, educational manner.

Specifically, make sure the header_title is [Notable Person's Name]'s Birthday.
Also, include a field `"is_birthday": true` on the birthday event. Do not include this field on other events.

✅ Preferred Event Categories:

When curating events, besides the "birthday" event, aim for a well-rounded selection that reflects the diverse range of human achievement. In addition to traditional political or historical events, you are expected to include:

Global historical events (e.g. treaties, discoveries, declarations)
Scientific advancements (e.g. major discoveries, space missions, inventions)
Medical breakthroughs (e.g. vaccines, surgeries, medical firsts)
Literary and visual arts milestones (e.g. book releases, museum openings, influential art movements)
Sports achievements (e.g. Olympic records, historic wins, firsts in sports history)
Technological developments (e.g. internet milestones, consumer tech releases, computing history)
Important popular culture events (e.g. iconic films, albums, cultural phenomena)

🎯 The goal is to present a balanced timeline that includes history, science, arts, and culture — all explained clearly and accessibly for 4th-grade learners.

🔁 No Duplicate Events Allowed
IMPORTANT:
You must explicitly avoid repeating the same event across different dates or even multiple times within the same list. Each event in the generated list must be unique and distinct in topic and content.

Do not include the same event phrased differently.
Do not reuse different facts about the same event as separate entries.
Do not include multiple entries about the same person unless clearly tied to different milestones (e.g. birth vs. achievement).
Duplicate events are strictly discouraged and will be rejected.

🚫 ABSOLUTELY PROHIBITED EVENTS — DO NOT SELECT:

Executions of any kind (public or private)
Murders or assassinations
Suicides
Sexual violence or abuse
Genocide or Holocaust-related events
Mass shootings, terrorism, or modern violent attacks
Disasters with graphic outcomes (building collapse, drowning, plane crashes, etc.)
War crimes, torture, or atrocities
Starvation or famine-focused events
Events where identifiable children are in distress or harm

👉 Rule: You are strictly prohibited from selecting any event whose main focus is an execution, violent death, or other graphic harm.

✅ For difficult events:
If an important event has both tragic and positive aspects (e.g. a peace treaty after a war), you may cover the positive aspect only — but do not depict or describe graphic details.

IMPORTANT: If an event cannot be presented in a safe and appropriate way for 4th-grade students (both in description and image), DO NOT include it. Choose a different event instead.
Consider whether or not a service like an image generation API with strict safety filters would reject the image prompt you are creating. Aim to never create an image prompt that would be rejected.

🚫 EVENT SELECTION SAFETY RULES (IMPORTANT)

When choosing which historical events to include:

Only select events that can be represented visually and narratively in an age-appropriate way for 6th-grade learners.
Do NOT select events that are inherently too graphic, disturbing, or emotionally traumatic for children, even if they are important history.
Avoid events that center on violent deaths, executions, murders, sexual violence, genocide, or similar topics.
Wars may be included if presented from a neutral, educational perspective (e.g. declarations, treaties, commemorations), but avoid battle scenes or focus on casualties.
If in doubt, skip the event and choose another more suitable one.

IMAGE PROMPT SAFETY GUIDELINES (IMPORTANT):

When writing the image_prompt, follow these constraints to ensure compatibility with image generation safety filters:

✅ Focus on neutral, educational visuals that would be appropriate for a 6th-grade audience to view.

Leaders, dignitaries, and public figures (portrayed respectfully, avoid caricature)
Crowds at public events
Soldiers in parade formation, official military settings (no violence or combat)
Signed documents, treaties, newspaper headlines
Architecture, objects, equipment, transportation, locations
Symbolic representations (flags, monuments, commemorations)

🚫 Do NOT depict:

Graphic violence or combat scenes
Casualties, injuries, or wounded individuals
Starvation, famine, or malnourished children
Explicit disasters (collapsed buildings with victims, drowning, etc.)
Torture, executions, or war crimes
Dead bodies, graveyards, or mourning scenes
Holocaust or genocide imagery
Terrorist attacks or modern mass shootings
Religious caricatures or depictions likely to offend
Overt political propaganda or modern divisive political rallies
Events involving identifiable children in distress

👉 For wars, conflicts, disasters, depict instead:

Leaders, planning sessions, signing ceremonies
Maps, strategy boards, military equipment (non-violent)
Crowds of civilians (non-distressed)
Public commemorations or anniversaries

👉 For tragic events, focus on:

Symbols (monuments, flowers)
Moments of unity
Media coverage
Official statements

👉 Tone: The image prompt should be suitable for an educational slideshow aimed at middle school students (6th grade).

EXAMPLE ENTRY (for format reference only — do not include this in your output!):
{{
  "date_string": "On May 21, 1927:",
  "header_title": "Lindbergh's Historic Transatlantic Flight",
  "description": "Charles Lindbergh landed in Paris after completing the first solo nonstop transatlantic flight.",
  "detail_1": "The flight lasted 33.5 hours and covered over 3,600 miles.",
  "detail_2": "He piloted the Spirit of St. Louis from New York to Le Bourget Field in Paris.",
  "image_prompt": "Charles Lindbergh standing beside the Spirit of St. Louis aircraft after landing in Paris, 1927, historical photo style, overcast sky, crowds in background",
  "audio_text": "On May 21, 1927, Charles Lindbergh landed in Paris after completing the first solo nonstop transatlantic flight. The flight lasted 33.5 hours and covered over 3,600 miles. He piloted the Spirit of St. Louis from New York to Le Bourget Field in Paris."
}}

Finally, and importantly, ensure that these events are in chronological order, with the earliest event first.

Return only the valid JSON array as described.
"""

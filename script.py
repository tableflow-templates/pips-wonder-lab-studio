# The Curiosity Crew — Episode 1: Why does ice float?
# Items: ("say", WHO, text, expr) | ("wait", seconds, tag) | ("tag", name)
# WHO in MIA, LEO, PIP, ALL

SCENES = [
  # 1. HOOK
  [("wait", 0.6, None), ("tag", "drop"), ("wait", 1.6, None),
   ("say", "LEO", "Plop! One ice cube for my lemonade.", None),
   ("say", "MIA", "Whoa! Look at that!", "surprised"),
   ("say", "LEO", "The ice is floating on top!", None),
   ("say", "MIA", "But why? Ice is hard, like a little rock.", None),
   ("say", "PIP", "Beep! Rocks sink. Ice floats. Mystery detected!", None),
   ("say", "MIA", "Let's find out!", None),
   ("tag", "title"), ("wait", 3.0, None)],
  # 2. THE MYSTERY
  [("wait", 0.5, None),
   ("say", "LEO", "Maybe ice has air inside, like a balloon!", None),
   ("tag", "bubble_leo"),
   ("say", "PIP", "Bzzt! Maybe ice is scared of the bottom of the glass?", None),
   ("tag", "bubble_pip"),
   ("say", "LEO", "Ha! Ice doesn't get scared, Pip.", None),
   ("say", "MIA", "Good guesses! But a real scientist does not just guess.", None),
   ("say", "MIA", "A real scientist tests!", None),
   ("wait", 0.6, None)],
  # 3. EXPERIMENT 1
  [("wait", 0.5, None),
   ("say", "MIA", "Experiment one! An ice cube and a pebble.", None),
   ("say", "MIA", "We drop them both into water.", None),
   ("tag", "drop1"), ("wait", 2.2, None),
   ("say", "LEO", "The pebble sinks down, down, down...", None),
   ("say", "LEO", "But the ice stays on top!", "surprised"),
   ("say", "PIP", "Beep! Ice is just frozen water.", None),
   ("say", "PIP", "And frozen water floats on liquid water!", None),
   ("say", "MIA", "So something about ice is different. Let's look closer!", None),
   ("wait", 0.6, None)],
  # 4. EXPERIMENT 2
  [("wait", 0.5, None),
   ("say", "LEO", "Experiment two! I fill an open cup with water.", None),
   ("tag", "fill"), ("wait", 1.5, None),
   ("say", "LEO", "Right up to this line.", None),
   ("say", "MIA", "Then we put it in the freezer.", None),
   ("say", "MIA", "Only open cups! Never freeze a closed bottle.", None),
   ("tag", "freezer"), ("wait", 1.0, None),
   ("say", "PIP", "Bzzt! Many hours later...", None),
   ("wait", 1.0, None), ("tag", "back"), ("wait", 0.8, None),
   ("say", "LEO", "Whoa! The ice is higher than the line!", "surprised"),
   ("say", "MIA", "When water freezes, it takes up more space.", None),
   ("say", "PIP", "Same water, more space. That means less density!", None),
   ("tag", "density"),
   ("say", "MIA", "Density means how tightly stuff is packed into its space.", None),
   ("wait", 0.8, None)],
  # 5. AHA!
  [("wait", 0.5, None),
   ("say", "MIA", "Water is made of tiny, tiny bits called molecules.", None),
   ("say", "LEO", "In liquid water, they crowd close together.", None),
   ("say", "LEO", "Like kids squeezing into a busy line!", None),
   ("tag", "ice"),
   ("say", "PIP", "Beep! When water freezes, they hold hands in rings.", None),
   ("say", "PIP", "Rings have more space inside!", None),
   ("say", "MIA", "So ice is less packed than water.", None),
   ("tag", "lab"),
   ("say", "MIA", "And less dense things float on top!", None),
   ("tag", "bulb"),
   ("say", "ALL", "Aha!", "surprised"),
   ("say", "LEO", "Just like a beach ball in a pool!", None),
   ("wait", 0.8, None)],
  # 6. TAKEAWAY
  [("wait", 0.5, None),
   ("say", "MIA", "Ice floats because it is less dense than liquid water.", None),
   ("tag", "lake"),
   ("say", "PIP", "Fun fact! In winter, lakes freeze on top first.", None),
   ("say", "PIP", "The ice is like a lid, and fish swim in the water below!", None),
   ("tag", "end"),
   ("say", "LEO", "What do you wonder about? Keep asking why!", None),
   ("say", "ALL", "Wonder Lab, mission complete!", None),
   ("wait", 2.5, None)],
]

def line_dur(text):
    words = len(text.split())
    return max(2.2, words / 2.4 + 0.9)

GAP = 0.35

def timeline(scene):
    """Return (lines, tags, duration). lines: list of (start, end, who, text, expr)."""
    t = 0.0; lines = []; tags = {}
    for it in scene:
        if it[0] == "wait":
            t += it[1]
            if it[2]: tags[it[2]] = t
        elif it[0] == "tag":
            tags[it[1]] = t
        else:
            d = line_dur(it[2])
            lines.append((t, t + d, it[1], it[2], it[3]))
            t += d + GAP
    return lines, tags, t

if __name__ == "__main__":
    tot = 0
    for i, s in enumerate(SCENES):
        l, tg, d = timeline(s)
        print(i + 1, round(d, 1), tg)
        tot += d
    print("total", round(tot, 1))

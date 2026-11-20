# Motion Offense Playbook

A phone- and tablet-friendly playbook and practice plan for a 7th grade girls basketball team running **4-out 1-in motion**. It switches to 5-out when the post is on the bench.

The site has four tabs:

- **Offense:** roles, the 5 rules, and an animated diagram for each rule
- **Plays:** Base Motion, Continuous Motion (5 trips with no shot), Dribble-At Backdoor, the "Post!" quick hitter, 5-Out, and vs 3-2 Zone
- **Drills:** every drill with animated diagrams
- **Practice:** the day's plan with a running practice clock and check-offs

## Making a new practice

```bash
python3 practice.py new 2026-11-24     # copies the latest practice to a new date
# edit practices/2026-11-24.json
python3 practice.py build              # rebuilds docs/
git add -A && git commit -m "Practice 11/24" && git push
```

The newest practice becomes the home page. Older practices stay linked at the bottom of the Practice tab.

**From your phone:** open `practices/` on github.com, copy a file into a new one named with the new date (or edit an existing one), and commit. The GitHub Action rebuilds the site automatically.

### Practice file format

```json
{
  "date": "2026-11-24",
  "title": "Motion vs pressure",
  "notes": "Optional note shown at the top of the Practice tab.",
  "blocks": [
    { "min": 10, "title": "Warm-up and form shooting", "drill": "warmup",
      "items": ["Dynamic warm-up", "Form shooting in pairs"] }
  ]
}
```

`drill` is optional. It adds a "See drill diagrams" link. Valid drills are `warmup`, `handling`, `passcut`, `backdoor`, `threeman`, `post`, `lowcut`, `deny`, `closeout`, `shell5`, `shell53` and `scrim`. Run `python3 practice.py list` to see each practice's total minutes.

To change plays, drills or the offense pages, edit `template.html`, then run `build`.

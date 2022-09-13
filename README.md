# RPI Ballroom Competition Scorekeeper
### Language: Python
#### UI Package: PyQt5?
<!--- ##### Files: gui.py, scorecard.py
## Features:
#### Scoring
- different scorecards to track callbacks and placing
- add multiple scorecards per round for each judge
- *for callbacks*: output numbers from most to least callbacks
- *for callbacks*: show total count of dancers at each amount of callbacks to determine future round size
- *for placing*: use skating system rules for placements
- *for placing*: display calculation table for placements of each couple
- displays callbacks and placing similar to o2cm
#### Saving
- allow user to name rounds by event number/round/dance
- backup rounds in th event of crashes or missing paper scoresheets
- save callbacks and placing results with appropriate labelling -->


## OVERHAUL
### Home Page
Introduce app!
Buttons:
- Start a new competition
- Load a previous competition
### Competition Page
Info to track:
- Comp name
- Day/date
- List of judges (include name and number)
- List of events (include number, level, and dance(s)
- Competition results locked (boolean, password protected)
Buttons:
- add new judge
- add new event
### Event Page
Info to track:
- Event number
- Level
- Dance(s)
- List of rounds
Buttons:
- add new round
### Round Page
Info to track:
- Event number
- Level
- Dance(s)
- Round
- List of judges/scorecards (by number)
- Results
- Results status (up to date/behind)
Buttons:
- add new scorecard
- remove scorecard
- recalculate results
### Scorecard Page
Info to track:
- Event number
- Level
- Dance(s)
- Round
- Judge number
### Judge Page
Info to track:
- name
- number
- list of scorecards (unmutable)


# RPI Ballroom Competition Scorekeeper
### Language of Choice: Python
#### UI Package: PyQt (or others)
## Possible Features:
#### Scoring
- keep heat lists for each round
- offer different scorecards to track callbacks and placing
- add multiple scorecards per round for each judge
- *for callbacks*: output numbers from most to least callbacks
- *for callbacks*: show total count of dancers at each callback level to determine future round size
- *for placing*: see skating system rules for feasibility
- *for placing*: display calculation table for placements of each couple
- linked dances must have combined callbacks
- look to O2CM for how to display callbacks and placing
#### Saving
- allow user to name rounds by round/dance/level/style/etc
- backup results to handle crashes
- save callback and placing results with appropriate labelling
- allow reload of previously saved results in case of error
#### Testing
- use previous O2CM results to confirm program function

# About
This github repo is a collection of python files and ipython notebooks that have resulted in
completed projects. Although I don't have a ton of time to work on this stuff, I hope to keep it
updated whenever I do. Please excuse some the poor style in the .py files and all of the
horrible style in the .ipynb files.
<br/>
My hope in making the code public is that a few people find this interesting enough to try to
replicate, and can either catch some bugs in my own work or do some interesting analysis of their
own. If you do, I would love to hear about it!
<br/>
Contact info:
<br/>
twitter: @aabsblog
<br/>
email: hw.chase.17@gmail.com

## Player compatibility (8/1/2018)
Presented as a poster at CASSIS 2018
<br/>
The premise of this project was to come up with some way of identifying player compatibility.
By compatibility I mean how well two player's style of play mesh. Specifically, to estimate the
`style of play` for each player I focus on only a subset of the possession - namely I only focus on
shots, ignoring turnovers, rebounds, etc. This is not because I don't think those things matter
for compatibility, but because I didn't have any novel modeling insights to bring there.

My `novel` modeling insight to model shots (if you can even call it that) was to condition on
knowing the player who is taking the shot, then estimate the location on the court (broken up into
seven distinct areas) from whence he would shoot, then, conditional on the location, estimate the
probability that he would make said shot. All the while, we are controlling for

1) who the player is
2) who his teammates are
3) who the opponents (defenders) are

This allows us to learn six sets of coefficients for each player

1) a player's tendency to shoot from each location on the court
2) a player's ability to score from each location on the court
3) a player's influence on his teammates' tendencies to shoot from each location
4) a player's influence on his teammates' ability to score from each location
5) a player's influence on his opponents' tendencies to shoot from each location
6) a player's influence on his opponents' ability to score from each location

In addition, I also included positional dummies to learn positional averages for all the above
(see poster for plots of those)
<br/>

Why is this helpful in modeling player compatility? Well, if you have a player who is really good
at scoring from the paint, you probably don't want to pair him with players who diminish their
teammates' tendencies to shoot from the paint. Practically, most big men are both good at scoring
(and tend to shoot) from the paint, while limiting their teammates tendencies (and ability) to score
from there. I think that makes sense - intuitively, there is should be some diminishing marginal
returns to having multiple big men who operate under the basket on the court.

<br/>
I've included below a link to the poster I presented, as well as links to notebooks where I did all
my work.

<br/>
[Link to poster](poster_07_31.pdf)

### Get annotated play by play data
Scrape play by play data from nba.stats.com, then annotate it with the players who were on the court at the time
<br/>
[Link to Notebook](player_compatibility_notebooks/play_by_play_with_lineups.ipynb)

### Get shot data
Scrape shot data from nba.stats.com, which contains information about where each shot was taken
<br/>
[Link to Notebook](player_compatibility_notebooks/player_shot_charts.ipynb)

### Merge data
Merge play by play and shot data so we have information about each shot as well as who was on the court at the time in one dataframe
<br/>
[Link to Notebook](player_compatibility_notebooks/join_shot_charts_play_by_play.ipynb)

### Build model(s)
Build main model and other models to compare it to
<br/>
[Link to Notebook](player_compatibility_notebooks/modeling.ipynb)

Thanks for reading!
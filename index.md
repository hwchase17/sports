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


## NFL QB Comps (April 2019)
NB: This is a fairly crude writeup. It is not a finished piece, I hope to finish it for NESSIS. But since the NFL draft is tomorrow I thought it would be timely to release this now. With that said, any feedback/questions would be greatly appreciated! In that vein, I am holding off for now on releasing all code but do plan to eventually!

### Introduction

The motivation for this project was to provide analytical comparisions for QBs as they are drafted. Draftniks love to make "pro comparisions" for players, so I thought it would be fun to do an analytical version of that.

My first issue was determining with statistics to look at, in order to judge how similar players were to eachother. There were about a million I could think of, and because I wanted to try to keep my views out of it (since I am not a football expert) I decided that I would first try to predict quarterback success in the NFL, and then use the feature importances/weights from that model to help determine how similar players were to eachother, with the theory that aspects of a player that helped them succeed in the NFL would also determine comparable players.

This work differs from previous work in several ways. One, I am creating analytical comparisions - most other similar works just tries to predict quarterback success. Two, I am choosing to include as many variables as I can think of and use LightGBM as a predictor, hoping to gain accurracy while realizing I am sacrificing interpretability. Most other works goes in the opposite direction, choosing simple models and a few variables. Finally, I am using a target that is somewhat unique (more on that below).

### Part 1: Choosing a target

Many other models use as a target some binary measurement, i.e. whether the player achieved above X AY/A in the NFL. I wanted to attempt to model a continuous target in order to try to glean the most information. However, choosing a good target is hard, and it is possible this was a bad decision. This is definitely one of the (potential) major flaws with this work (not a great way to start, I know).

When choosing a continuous target, there are several things I kept in mind. If I choose a 'count' statistic, like games played or touchdowns, older players who have been in the league longer would be overweighted. If I chose a rate statistic, however, like AY/A or passing %, it would not properly reward longevity.

I use as a basis for my target AV from pro-football-reference. (As a side note, all stats are pulled from there, and its cousing site for college football stats. They are a great set of sites). I then normalize in two ways. One way is by calculating the rank of accumulated AV for the player compared against all other players (normalized between 0 - 1, with 1 being the best). Secondly, I calculated the rank of accumulated AV for the player compared to players when they had been in the league for as long as they had. I then combined these two scores to get their final score, which is what I would be trying to predict. The first way is to reward longevity, the second way is to (hopefully) not overly penalize only being in the league for a short time.

As an example, consider Baker Mayfield. Last year he put an AV of 10. Among all QBs, this puts him in the 57th percentile. Among all QBs after their first year, this puts him in the 95th percentile. Combining these, he gets a grade of .76. (A fun side effect of this target is that being on a scale of 0 - 1 means that if you multiply by 100 their scores are often very similar to a madden rating).

By this metric, the top players of all time are: Peyton Manning, Tom Brady, Drew Brees, Brett Farve, Fran Tarkenton, Dan Marino, John Elway, etc...

Importantly to note, when backtesting is performed, these scores are recalculated for year, as a point in time estimate of what it would have appeared like had we actually made predictions then.

### Part 2: Creating features

As mentioned before, all features were created based on stats pulled from https://www.sports-reference.com/cfb/. The types of features can be grouped in various categories:

Basic stats: things like passing rating, yards, touchdowns, AY/A, rushing yards, etc. I included both their career totals and their totals for the season before they turned pro.

Schedule statistics: things like SRS, SOS, conference average SRS, SRS over last 10 years for their school... an attempt to tell the model about the difficulty level of the competition that the quarterback was facing.

Player summary stats: loosely, things like years played, years started, years above 60% passing percentage, years playing a tough schedule, what year they were when they went pro, ratio of pass to run, etc.

Awards stats: hiesman voting stats, all american awards, both for them and their teammates and players in their conference on offense and defense.

### Part 3: Modeling and similarity scores

I used LightGBM, a gradient boosting framework. I used heavy regularization, including imposing monotonicity constraints on most variables, which helped significantly.

I considered modeling the probability of playing in the NFL separately from a players expected score, should they play in the NFL, and then combining the results, but found that that produced results not significantly better than just modeling everything together.

How did I get similarity scores from this? For a given player, I looked at which players they ended up in the same leaf as. Specifically, if the final model was ten trees, and player A ended up in the same leaf as player B in 6 of the ten decision trees, their similarity score would be 60%.

### Part 4: Results

I have uploaded a full csv of backtest results from 1980 to present [here](https://github.com/hwchase17/sports/blob/master/nfl_qb_comps/backtest_results_nfl_qbs.csv). To quickly highlight some points:

Biggest misses, part 1 (Model predicted bust, actually star): Brett Farve, Matt Hasselbeck, Jeff Garcia, Randall Cunningham, Trent Green, Mark Brunell

Biggest misses, part 2 (Model predicted star, actually bust): Colt Brennan, Charlie Ward, Mason Mudolph, Josh Heupel, Trevone Boykin

Highest predicted (definite skew towards recent players): Andre Ware, Baker Mayfield, Marcus Mariota, Johnny Manziel, Deshaun Watson, Rodney Peete, Drew Brees, Steve Walsh, Brady Quinn, Chase Daniel, Troy Aikman

I have not included historical pro comparisions although I can provide on request.

### Part 5: 2018 predictions

Follow me on twitter (@aabsblog) to see these in real time!

## Player compatibility (8/1/2018)
Presented as a poster at CASSIS 2018
<br/>
The premise of this project was to come up with some way of identifying player compatibility.
By compatibility I mean how well two player's style of play mesh. Specifically, to estimate the
`style of play` for each player I focus on only a subset of the possession - namely I only focus on
shots, ignoring turnovers, rebounds, etc. This is not because I don't think those things matter
for compatibility, but because I didn't have any novel modeling insights to bring there.

<br/>
My `novel` modeling insight to model shots (if you can even call it that) was to condition on
knowing the player who is taking the shot, then estimate the location on the court (broken up into
seven distinct areas) from whence he would shoot, then, conditional on the location, estimate the
probability that he would make said shot. All the while, we are controlling for

1. who the player is
2. who his teammates are
3. who the opponents (defenders) are

This allows us to learn six sets of coefficients for each player

1. a player's tendency to shoot from each location on the court
2. a player's ability to score from each location on the court
3. a player's influence on his teammates' tendencies to shoot from each location
4. a player's influence on his teammates' ability to score from each location
5. a player's influence on his opponents' tendencies to shoot from each location
6. a player's influence on his opponents' ability to score from each location

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

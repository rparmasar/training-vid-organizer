# user-workflows

## rough architecture

mainly will have these components:

* the cli
* sqlite database for storing video metadata
* some filesystem (will usually be my ssd)

the filesystem should be where the videos will be actually stored, and the sqlite db is for tracking the important metadata about the videos. 

## file things

the video files are quite large so keeping them in a flat list on the ssd works here because we'll maintain our metadata in the sqlite db.

here is an example of the filename when downloaded from the camera - `20260921165522NORM0064.MP4`

## sqlite database

### current state

this is roughly the table from the `training_log` worksheet (`tests/sample_data/training_log.csv`) and it has the following columns:

* `date` - the date of the lift in YYYY-MM-DD format

* `bodyweight` - bodyweight before gym session

* `lift` - name of the lift (front_squat, overhead_press, deadlift, squat, bench, zercher_squat, incline_bench, zercher_deadlift)

* `top set weight` - weight of the heaviest set

* `top set reps` - reps with `top set weights` during the set

* `program` - name of program (separated by blocks e.g. 531-{1,3,5}+ and cp-w{1-10})

* `est. 1 RM` - calculated field - uses a formula to estimate the one rep max using `top_set_weight` and `top_set_reps`

* `year-month` - calculated year-month of `date`

* `program-iteration` - a count of the training macro cycles (used to compare 1 RMs + bodyweight between cycles)

### what to change

there are videos of warm-ups and back-off sets and some accessories not captured so we'll need to adjust the schema to handle those, something like:

* `top set weight` -> `weight`
* `top set reps` -> `reps`
* a flag for `top_set` of the session
* `reps_in_reserve` - measures how much extra reps for a `lift` subjectively (cap at 5+)
* `filepath` - path to the original video file
* an auto-maintained `id` column
 
## typical interactions for managing files / videos

### processing new videos (single)

1. download from camera to ssd in target folder
2. run something like `tvo add lift` that takes a `filepath` and the metadata args `date`, `bodyweight`, `lift`, `weight`, `reps`, `reps_in_reserve`, `program`, `program_iteration` and adds a new entry to the database (one table for now)

### processing new session (a collection of videos)

1. download multiple from camera to ssd in target folder
2. should be an option to do `tvo add session` and: 
   1. pass a config json (with full params for multiple calls to `tvo add`)
   2. pass an `--infer` flag + the config and let the cli figure out return a list of files not processed and then process them (can assume order matches config)

### find videos

some way to basically query the database from the cli and display results in terminal

### updating an entry (single)

changes the row for a given `id`

## typical interactions for analysis

### look at different videos for a given property

ideally, I want to be able to compare videos for any given property doing something like:

1. group by some property
2. return video files / open them in file viewer 

**out-of-scope for now** but later on, bringing the analysis from the spreadsheet would be cool i.e.:

1. performance per program
2. bodyweight over time
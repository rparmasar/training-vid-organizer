# future features

## calculated views  

these are metrics computed from the data in the db and should

### metrics to include

> **note:** implement these as calculated VIRTUAL cols in db (this may mean we need a separate dataclass from `LiftEntry` to capture these returned values e.g. `LiftResult`? or we can handle them like `entry_id`)

* `estimated_1rm` - estimated one rep max using Bryzycki method ${\displaystyle w\cdot {\frac {36}{37-r}}={\frac {w}{{\frac {37}{36}}-{\frac {1}{36}}r}}\approx {\frac {w}{1.0278-0.0278r}}}$

* `total_set_volume` - `weight` * `reps` for a given set to use as a measure of overall work done. this might be more helpful for comparing program iterations across the same lift.

### running comparison analysis

should be able to do some thing like `tvo analyze 1rm` and that runs the basic analysis between program iterations, which would be a query like:

```sql
SELECT 
    program_iteration, 
    lift,
    AVG(estimated_1rm) as avg_estimated_1rm, 
    AVG(bodyweight) as avg_bodyweight
GROUP BY program_iteration, lift
ORDER BY program_iteration DESC
```

and maybe something like `tvo analyze total_set_volume` would be a query like:

```sql
SELECT
    program_iteration,
    lift,
    AVG(total_set_volume) as avg_total_set_volume,
    AVG(bodyweight) as avg_bodyweight
GROUP BY program_iteration, lift
ORDER BY program_iteration DESC
```

## auto-ingesting files + processing

should look like:

1. xtu-go camera plugged into laptop + session json filled out
2. run some command which: 
   1. maps the files to the `filename` attribute in the session json (can assume the order of the session json will match the order of the videos)
   2. transfers the files to the ssd
   3. adds the session json to the database

## interaction with the google sheet?

currently, the google sheet is used for:

1. tracking top set performance
2. generating 531 programs
3. running basic analysis which compares the avg. est. 1 rm for each lift across each program iteration

how should that change now that this tool is a thing? -> can use [`gspread`](https://docs.gspread.org/en/latest/) to export training db into a google sheet.

so new process would look like:

* the local sqlite database is the source of truth and contains warm-up sets, top sets, back-off sets, and other recorded lifts.
* on some basis (or via something like `tvo export`), the database info is exported to the google sheet. (this means i can view the analysis portion from anywhere)
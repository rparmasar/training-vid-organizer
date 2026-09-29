# release_notes-1.0.0

## overview

this documents what's done and what is remaining for release `1.0.0`

## what's done

todo

## what is outstanding

### core features

* [done] resetting db
* [done] update + deleting rows in db (maybe expose a query command for advanced usecases that just executes UPDATE statements?)
* [in-progress] opening video files based on results of `list lifts` command
* add help text for commands + options

### dev-ops related

* implement build script / github actions to build package
* test installing with wheel in fresh virtual env

### one-time batch job

* load training log data into database (only captures top sets)
* load data for lifts with videos into database (some overlap with training log but this includes warm-ups and one-off lifts, also not all lifts are recorded)

## later

* file renaming? -> rename video files using metadata
* calculated table to store analysis cols e.g. estimated 1 RM, total weight volume? (reps\*weights\*sets)


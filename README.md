# MrSpice-CLI
A CLI for ETL jobs used to prepare recipe data for the Mr Spice recommendation engine.

Querying ingredient recommendations is hard work for mongo, so I wrote this suite of CLI tools to pre-calculate the `MrSpice score` for every possible combination of ingredients of size `r`.

## Getting Started
- Install dependencies: `pip install -r requirements.txt`
- Startup a mongo db instance on `localhost:27017`
- Populate the database with the recipe data set of your choice

## Features
- a handy dandy live updating progress bar

`49.85% | Est. remaining: 00:00:00:07 | Elapsed: 00:00:00:07 | Est. Total: 00:00:00:14`

## Usage

### sample
From the `SOURCE` collection, insert into the `DESTINATION` collection a random sample of size `SIZE`

```
Usage: mrspice-cli.py sample [OPTIONS] DATABASE SIZE SOURCE DESTINATION

Options:
  --host TEXT     database host
  --seed INTEGER  seed for the random generator
  --help          Show this message and exit.
```

### count_and
For every possible combination of ingredients of size `r_min` to `r_max`, count the number of recipes in the `RECIPES` collection that contain that combination of ingredients. Insert the combinations into the `COMBINATIONS` collection.

```
Usage: mrspice-cli.py count_and [OPTIONS] DATABASE RECIPES COMBINATIONS

Options:
  --host TEXT      database host
  --skip INTEGER   number of recipes to skip in the source
  --r_min INTEGER  minimum combination size to pre-calculate
  --r_max TEXT     maximum combination size to pre-calculate
  --help           Show this message and exit.
```

### count_or
Given a `COMBINATIONS` collection of `and-counts`, use the [inclusion-exclusion principle](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle) to update each of the combinations of size `r_min` to `r_max` with the count of recipes that contain any of the combination's ingredients (the `or-count`).

```
Usage: mrspice-cli.py count_or [OPTIONS] DATABASE COMBINATIONS

Options:
  --host TEXT      database host
  --skip INTEGER   number of recipes to skip in the source
  --r_min INTEGER  minimum combination size to pre-calculate
  --r_max TEXT     maximum combination size to pre-calculate
  --help           Show this message and exit.
```

### link
Given a `COMBINATIONS` collection of `and-counts` and `or-counts`, update each combination with a list of references to other combinations that are of size `r + 1` and include all ingredients from the given combination.

```
Usage: mrspice-cli.py link [OPTIONS] DATABASE COMBINATIONS

Options:
  --host TEXT      database host
  --skip INTEGER   number of recipes to skip in the source
  --r_min INTEGER  minimum combination size to pre-calculate
  --r_max TEXT     maximum combination size to pre-calculate
  --help           Show this message and exit.
```

### sort
Given a `COMBINATIONS` collection of `and-counts` and `or-counts` that have been `linked`, sort each combination's references by their `MrSpice score`.

```
Usage: mrspice-cli.py sort [OPTIONS] DATABASE COMBINATIONS

Options:
  --host TEXT      database host
  --skip INTEGER   number of recipes to skip in the source
  --r_min INTEGER  minimum combination size to pre-calculate
  --r_max TEXT     maximum combination size to pre-calculate
  --help           Show this message and exit.
```

### precalc
Runs all of the above jobs in order.

```
Usage: mrspice-cli.py precalc [OPTIONS] DATABASE RECIPES COMBINATIONS

Options:
  --host TEXT      database host
  --skip INTEGER   number of recipes to skip in the source
  --r_min INTEGER  minimum combination size to pre-calculate
  --r_max TEXT     maximum combination size to pre-calculate
  --help           Show this message and exit.
```

### populate_graph
Migrate the recipes from the `RECIPES` collection to a ne04j database

```
Usage: mrspice-cli.py populate_graph [OPTIONS] DATABASE RECIPES

Options:
  --host TEXT     mongo host
  --neoHost TEXT  neo4j host
  --help          Show this message and exit.
```

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
Given a `COMBINATIONS` collection of `and-counts` and `or-counts`, update each combination of size `r` with a list of references to other combinations that are of size `r + 1` and contain all ingredients from the given combination.

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
Given a `COMBINATIONS` collection of `and-counts` and `or-counts` that have been `linked`, sort each combination's references by their `MrSpice score`. The `MrSpice score` of a given combination is the probability that you will find every ingredient of the given combination contained in a recipe, given that you have selected a recipe containing at least one ingredient of the given combination.

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

## Designing a Pairing Metric

The goal of Mr.Spice is to help users develop a "sense" of which ingredients pair well with others. As I do not have a ML or DS background, my first naive approach was to take a given ingredient and count the frequency with which other ingredients occur with it. The more frequently the ingredients co-occur in recipes, the better the "match". The problem with this approach is that butter and salt always top the list. While it may be true that butter and salt go with everything, that information does not improve one's "sense" of which ingredients pair well together.

A more meaningful metric would be one that ranks those ingredients that match frequently with each other, but less frequently with other ingredients. The ratio of the number of recipes that contain both ingredients vs the number of recipes that contain either ingredient would balance out butter and salt. You could call this the count of recipes that contains ingredient one AND ingredient two, divided by the count of recipes that contain ingredient one OR ingredient two. Since butter and salt occur in most recipes, their OR count with any given ingredient would be very high, thus watering down the score. This brings ingredients that are more "faithful" to the top of the results. 

Another advantage of this metric is that it can be calculated for any number of input ingredients. I.e., you can input both avocado and red onion. To calculate the score for avocado, red onion, and cilantro you just need the count of recipes that contain avocado AND red onion AND cliantro as well as the count of recipes that contain avocado OR red onion OR cilantro.

The metric was good but it turns out that producing the results is quite costly. When calculating the ranked list, each candidate ingredient has to query the recipes database for the AND count and the OR count. Counting queries are not cheap and both to be performed for each ingredient that co-occurs with the given ingredient.

The current solution to this is to pre-calculate the AND and OR counts and store them in a separate collection. This is probably not the best solution as it gets kind of ridiculous generating every possible combination of ingredients. Once you get to calculating all possible combinations of 5 or more ingredients, the number of combinations is in the trillions. 

For now the idea is that all combinations of up to 3 ingredients gets precalculated in this way. Queries that give 4 or more ingredients will need to be calculated on the fly. The more ingredients you give to the system, the fewer recipes there are that contain all of those ingredients, so queries containing four or more given ingredients tend to be less costly to query for on the fly.


## Using the CLI to PreCalculate

Lucky for you I wrote a CLI that does these precalculation jobs. I will give you a dump of the recipes collection which is actually quite small. You will want to first run the `sample` job to take a smaller sample of the 400k recipes. I recommend 10k.

```
python mrspice-cli.py sample yummly 10000 recipes recipes10k
```
This assumes that you are running the mongoDB locally at localhost:27017, your database is called `yummly`, your recipes collection is called `recipes` and you want to name the collection of your sample recipes `recipes10k`.

Now that you have taken a nice dev-sized sample of the recipe dataset, we can run the precalc job. 

```
python mrspice-cli.py precalc r_max=3 yummly recipes10k combinations10k
```
This assumes that you are running the mongoDB locally at localhost:27017, your database is called yummly, the recipes colection that you want to pre-calc scores for is called `recipes10k`, and the collection that you want to name the collection of precalculated scores `combinations10k`. r_max=3 is very important. This tells the system to only pre-calculate combinations up to length 3. Putting a larger number here will result in very long jobs and collections tens of GB large.

A convenient progress bar will let you know how long each precalc job is going to take.

Once you have the precalc job done, you just need to change the config in the API to point to the `recipes10k` and `combinations10k` collections.
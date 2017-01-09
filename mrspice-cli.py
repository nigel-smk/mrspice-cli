import click
import time

import output
import progress_bar
import sample_service
from and_count_service import AndCountService
from or_count_service import OrCountService
from link_service import LinkService
from index_service import IndexService
from sort_service import SortService

# TODO validate arguments and options here


@click.group()
def dbutils():
    pass


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--seed', default=0, help='seed for the random generator')
@click.argument('database')
@click.argument('size')
@click.argument('source')
@click.argument('destination')
def sample(**kwargs):
    # Copy a random sample of the mongo records to another database
    sample_service.sample_collection(**kwargs)


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1)
@click.option('--r_max')
@click.argument('database')
@click.argument('recipes')
@click.argument('combinations')
def count_and(**kwargs):
    AndCountService(**kwargs).count_and()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1)
@click.option('--r_max')
@click.argument('database')
@click.argument('combinations')
def count_or(**kwargs):
    OrCountService(**kwargs).count_or()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1)
@click.option('--r_max')
@click.argument('database')
@click.argument('combinations')
def link(**kwargs):
    LinkService(**kwargs).link()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1)
@click.option('--r_max')
@click.argument('database')
@click.argument('combinations')
def link(**kwargs):
    SortService(**kwargs).sort_pairings()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1)
@click.option('--r_max')
@click.argument('database')
@click.argument('recipes')
@click.argument('combinations')
def precalc(**kwargs):
    start = time.time()
    IndexService(**kwargs).index()
    AndCountService(**kwargs).count_and()
    OrCountService(**kwargs).count_or()
    LinkService(**kwargs).link()
    end = time.time()
    elapsed = progress_bar._format_time(end - start)
    output.push("Total elapsed: {elapsed}".format(elapsed=elapsed))


if __name__ == '__main__':
    dbutils()

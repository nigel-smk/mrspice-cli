import time

import click
from common import output
from services import sample_service
from services.index_service import IndexService
from services.link_service import LinkService
from services.or_count_service import OrCountService
from services.populate_graph_service import PopulateGraphService
from services.sort_service import SortService
from services.yummly_ingredients_service import YummlyIngredientsService

from common import progress_bar
from services.and_count_service import AndCountService
from services.usda_service import USDAService


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
@click.option('--r_min', default=1, help='minimum combination size to pre-calculate')
@click.option('--r_max', help='maximum combination size to pre-calculate')
@click.argument('database')
@click.argument('recipes')
@click.argument('combinations')
def count_and(**kwargs):
    AndCountService(**kwargs).count_and()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1, help='minimum combination size to pre-calculate')
@click.option('--r_max', help='maximum combination size to pre-calculate')
@click.argument('database')
@click.argument('combinations')
def count_or(**kwargs):
    OrCountService(**kwargs).count_or()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1, help='minimum combination size to pre-calculate')
@click.option('--r_max', help='maximum combination size to pre-calculate')
@click.argument('database')
@click.argument('combinations')
def link(**kwargs):
    LinkService(**kwargs).link()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1, help='minimum combination size to pre-calculate')
@click.option('--r_max', help='maximum combination size to pre-calculate')
@click.argument('database')
@click.argument('combinations')
def sort(**kwargs):
    SortService(**kwargs).sort_pairings()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1, help='minimum combination size to pre-calculate')
@click.option('--r_max', help='maximum combination size to pre-calculate')
@click.argument('database')
@click.argument('recipes')
@click.argument('combinations')
def precalc(**kwargs):
    start = time.time()
    IndexService(**kwargs).index()
    AndCountService(**kwargs).count_and()
    OrCountService(**kwargs).count_or()
    LinkService(**kwargs).link()
    SortService(**kwargs).sort_pairings()
    end = time.time()
    elapsed = progress_bar._format_time(end - start)
    output.push("Total elapsed: {elapsed}".format(elapsed=elapsed))


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.argument('database')
@click.argument('collection')
def usda_foods(**kwargs):
    USDAService(**kwargs).get_foods()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.argument('database')
@click.argument('collection')
def fetch_yum_ingts(**kwargs):
    YummlyIngredientsService(**kwargs).get_ingredients()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='mongo host')
@click.option('--neoHost', default='http://neo4j:1234@localhost:7474/db/data', help='neo4j host')
@click.argument('database')
@click.argument('recipes')
def populate_graph(**kwargs):
    PopulateGraphService(**kwargs).populate()

if __name__ == '__main__':
    dbutils()

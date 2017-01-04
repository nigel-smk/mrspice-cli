import click
import sample_service
from and_count_service import AndCountService
from or_count_service import OrCountService
import tokenize_service


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
@click.argument('source')
@click.argument('destination')
def count_and(**kwargs):
    AndCountService(**kwargs).count_and()


@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of recipes to skip in the source')
@click.option('--r_min', default=1)
@click.option('--r_max')
@click.argument('database')
@click.argument('source')
def count_or(**kwargs):
    OrCountService(**kwargs).count_or()

@dbutils.command()
@click.option('--host', default='mongodb://localhost:27017', help='database host')
@click.option('--skip', default=0, help='number of combinations to skip in the source')
@click.option('--r_min', default=1)
@click.option('--r_max')
@click.argument('database')
@click.argument('source')
def tokenize(**kwargs):
    tokenize_service.tokenize(**kwargs)

if __name__ == '__main__':
    dbutils()

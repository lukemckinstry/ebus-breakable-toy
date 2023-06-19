import click
from django_api import DjangoAPI


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")
    api = DjangoAPI()
    agency_list = api.get("agency")
    print("agencies in DB ", agency_list)

if __name__ == '__main__':
    hello()


    #python hello.py --count=3
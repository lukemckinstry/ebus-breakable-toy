import click
from django_api import DjangoAPI


@click.command()
@click.option('--count', default=3, help='Number of greetings.')
@click.option('--name', default="Luke",
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")
    # api = DjangoAPI()
    # agency_list = api.get("agency")

    # print("agency_list --> ",  agency_list.json())

    
    # sample_agency_id = agency_list.json()[0]

    
    # data = {
    #     "type": "Feature",
    #     "geometry": { "type": "MultiLineString",
    #         "coordinates": [
    #             [ [100.0, 0.0], [101.0, 1.0] ],
    #             [ [102.0, 2.0], [103.0, 3.0] ]
    #     ] }
    #     ,
    #     "properties":
    #     {
    #         "route_id": "999",
    #         "route_short_name": "W",
    #         "route_long_name": "W",
    #         "route_desc": "",
    #         "route_type": "3",
    #         "route_url": "http://realtime.catabus.com/InfoPoint/46",
    #         "route_color": "999900",
    #         "route_text_color": "FFFFFF",
    #         "route_sort_order": "21",
    #         "route_distance": 41527.6023805,
    #         "trips_monday": 0,
    #         "trips_tuesday": 0,
    #         "trips_wednesday": 0,
    #         "trips_thursday": 0,
    #         "trips_friday": 0,
    #         "trips_saturday": 0,
    #         "trips_sunday": 0,
    #         "zev_charging_infrastructure": False,
    #         "zev_notes": None,
    #         "pct_zev_service": None,
    #         "num_zev": None
    #     }
    # }

    # print("sample agency ", sample_agency_id)

    # response = api.post("agency/925f12a7-1c44-4c1a-845c-ec8f8975bfc7/batch/route", data)

    # print("response --> ", response)


if __name__ == '__main__':
    hello()


    #python hello.py --count=3
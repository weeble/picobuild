import click


@click.group()
def main():
    pass


@main.command('frob')
@click.option('--widget-id')
def frob(widget_id):
    click.echo(f'widget-id: {widget_id}')


if __name__ == '__main__':
    main()

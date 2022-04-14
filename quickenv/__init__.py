#! /usr/bin/env python3

import os
import venv
import subprocess
import sys
import shutil

import click

@click.group()
@click.option(
    '-p',
    '--path',
    type=click.Path(exists=False, dir_okay=True, file_okay=False),
    default=os.environ.get('QUICKENV_DIRECTORY', os.path.join(os.path.expanduser('~'), '.quickenvs'))
)
@click.pass_context
def cli(ctx, path):
    """
    Manages Python virtual environments.

    You can provide the path that venvs will be stored in
    or set it as the 'QUICKENV_DIRECTORY' environment variable.

    By default, venvs will be stored in '~/.quickenvs'.
    """
    if not os.path.exists(path):
        os.makedirs(path)
    ctx.obj = {'path': path}

@cli.command()
@click.option(
    "-d",
    "--description",
    type=str,
    help="Description for the environment."
)
@click.option(
    "-a",
    "--alias",
    type=str,
    help="Specify a custom alias (otherwise it will be the name of the venv)."
)
@click.argument('name')
@click.pass_context
def create(ctx, name, description=None, alias=None):
    """
    Creates a new virtual environment.
    """
    if ' ' in name:
        click.echo("Error: Virtual environment names cannot contain spaces.")
        sys.exit(1)

    alias = alias if alias is not None else name
    if ' ' in alias:
        click.echo("Error: Aliases cannot contain spaces.")
        sys.exit(1)

    path = ctx.obj['path']
    venv_path = os.path.join(path, name)
    if os.path.exists(venv_path):
        click.echo('A virtual environment with this name already exists.')
        sys.exit(126)

    bash_aliases = os.path.join(os.path.expanduser('~'), '.bash_aliases')
    with open(bash_aliases, 'r') as f:
        for line in f.readlines():
            if line.startswith('alias {}='.format(alias)):
                click.echo(f"Alias '{alias}' is already in use.")
                sys.exit(126)

    click.echo("Creating...")
    venv.create(venv_path, with_pip=True)
    click.echo("Upgrading pip and setuptools...")
    subprocess.check_call([os.path.join(venv_path, 'bin', 'pip'), 'install', '-U', 'pip', 'setuptools'])

    description = "No description provided" if description is None else description
    with open(os.path.join(venv_path, 'description.txt'), 'w') as f:
        f.write("Created by quickenv script\n")
        f.write(description + '\n')

    with open(bash_aliases, 'a') as f:
        f.write(f'alias {alias}=". {venv_path}/bin/activate"\n')

    with open(os.path.join(venv_path, 'alias.txt'), 'w') as f:
        f.write("Created by quickenv script\n")
        f.write(alias + '\n')

    click.echo(
        f"Done. Source '~/.bash_aliases' or start a new shell and run '{alias}' to activate the venv."
    )
    sys.exit(0)


@cli.command()
@click.argument('name')
@click.pass_context
def delete(ctx, name):
    """
    Deletes a virtual environment.
    """
    path = ctx.obj['path']
    venv_path = os.path.join(path, name)
    if not os.path.exists(venv_path):
        click.echo('A virtual environment with this name does not exist.')
        sys.exit(126)

    with open(os.path.join(venv_path, 'alias.txt'), 'r') as f:
        alias = f.readlines()[1].strip()

    with open(os.path.join(os.path.expanduser('~'), '.bash_aliases'), 'r') as f:
        lines = [l for l in f.readlines()
                 if not l.startswith(f'alias {alias}=". {venv_path}/bin/activate"')]

    with open(os.path.join(os.path.expanduser('~'), '.bash_aliases'), 'w') as f:
        f.writelines(lines)

    shutil.rmtree(venv_path)
    click.echo(f'Deleted "{name}"')


@cli.command()
@click.pass_context
def list(ctx):
    """
    Lists all virtual environments.
    """
    path = ctx.obj['path']
    ls = os.listdir(path)
    if not ls:
        click.echo('No virtual environments found.')
        sys.exit(126)
    for name in sorted(ls):
        venv_path = os.path.join(path, name)
        if os.path.isdir(venv_path):
            with open(os.path.join(venv_path, 'description.txt'), 'r') as f:
                description = f.readlines()[1].strip()
            with open(os.path.join(venv_path, 'alias.txt'), 'r') as f:
                alias = f.readlines()[1].strip()
            click.echo(f"{name} (alias: {alias})")
            click.echo(f"  {description}")

if __name__ == '__main__':
    cli()

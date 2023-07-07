# Copyright (c) 2023 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Commit Message Validator.
#
# Commit Message Validator is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Commit Message Validator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Commit Message Validator.  If not, see <http://www.gnu.org/licenses/>.
import click
import click_aliases
from click_option_group import MutuallyExclusiveOptionGroup
from click_option_group import optgroup

from .hooks import install
from .lint import sample
from .lint import validate
from .version import __version__


@click.group(
    invoke_without_command=True,
    epilog="When no COMMAND is specified, we default to 'validate'",
    cls=click_aliases.ClickAliasedGroup,
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """Validate git commit messages to Wikimedia standards."""
    if ctx.invoked_subcommand is None:
        # Legacy default is to run the validate subcommand
        ctx.invoke(validate)


@cli.command("install-hook", aliases=["install"])
def install_hook():
    """Install commit-message-validator as a git post-commit hook."""
    return install()


@cli.command("validate", aliases=["lint"])
@optgroup("Validation standard", cls=MutuallyExclusiveOptionGroup)
@optgroup.option(
    "--gerrit",
    "validator",
    help="Use Gerrit standard",
    flag_value="GerritMessageValidator",
    default=False,
)
@optgroup.option(
    "--github",
    "validator",
    help="Use GitHub standard",
    flag_value="GitHubMessageValidator",
    default=False,
)
@optgroup.option(
    "--gitlab",
    "validator",
    help="Use GitLab standard",
    flag_value="GitLabMessageValidator",
    default=False,
)
def validate_message(validator=None):
    """Validate commit message(s)."""
    return validate(validator=validator)


@cli.command("sample")
@click.argument(
    "repo",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.argument("count", type=int, default=10)
def sample_repo(repo, count):
    """Sample commits in a repo to see if they pass validation.

    \b
    REPO is the filesystem path to the git repo to check.
    COUNT is the number of commits to sample (default: 10).
    """
    click.echo(f"Checking the last {count} commits to {click.format_filename(repo)}")
    return sample(repo, count)


if __name__ == "__main__":
    cli()  # pragma: nocover

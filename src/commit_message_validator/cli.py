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
import pathlib
import textwrap

import click
import click_aliases
from click_option_group import MutuallyExclusiveOptionGroup
from click_option_group import optgroup

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


@cli.command("install")
@click.pass_context
def install_hook(ctx):
    """Explain that this sub-command has been removed"""
    click.echo(
        click.style(
            textwrap.fill(
                "Support for this method of pre-commit hook installation "
                "has been removed.",
            ),
            fg="red",
        ),
    )
    click.echo(
        textwrap.fill(
            "See the README for instructions on installing as a "
            "https://pre-commit.com/ plugin",
            break_on_hyphens=False,
        ),
    )
    ctx.exit(1)


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
@click.option(
    "-m",
    "--merge-target",
    "merge_target",
    envvar=["CI_MERGE_REQUEST_DIFF_BASE_SHA", "GITHUB_BASE_REF"],
    default="HEAD~1",
    help="Verify all commits since current branch forked from the given target.",
)
@click.option(
    "--head",
    default="HEAD",
    envvar=["CI_COMMIT_SHA", "GITHUB_SHA", "GIT_COMMIT"],
    help="Head of current branch.",
)
@click.option(
    "--commit-msg-filename",
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
    help="Path to a file containing a commit-msg.",
)
@click.pass_context
def validate_message(
    ctx,
    validator=None,
    merge_target=None,
    head=None,
    commit_msg_filename=None,
):
    """Validate commit message(s)."""
    ctx.exit(
        validate(
            start_ref=head,
            end_ref=merge_target,
            msg_path=commit_msg_filename,
            validator=validator,
        ),
    )


@cli.command("sample")
@click.argument(
    "repo",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.argument("count", type=int, default=10)
@click.pass_context
def sample_repo(ctx, repo, count):
    """Sample commits in a repo to see if they pass validation.

    \b
    REPO is the filesystem path to the git repo to check.
    COUNT is the number of commits to sample (default: 10).
    """
    click.echo(f"Checking the last {count} commits to {click.format_filename(repo)}")
    ctx.exit(sample(repo, count))


if __name__ == "__main__":
    cli()  # pragma: nocover

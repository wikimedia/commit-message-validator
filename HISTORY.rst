#######
History
#######

All notable changes to this project will be documented in this file.

This project adheres to `Semantic Versioning`_.

`2.2.0`_ - 2025-10-27
---------------------
* Use ``CI_MERGE_REQUEST_REF_PATH`` as the source ref for compatibility with
  merge requests from forks. (Dan Duvall)

`2.1.0`_ - 2024-05-24
---------------------
* Prepare ``--commit-msg-filename`` input in the style of
  ``git commit --cleanup=strip`` (Bryan Davis)
* "Footer" references in code and docs changed to "trailer" to match git's own
  naming for structured commit message data. (Bryan Davis)
  (<https://git-scm.com/docs/git-interpret-trailers>). (Bryan Davis)
* T360460: Fix exit status regression in legacy ``commit-message-validator``
  invocation. (Bryan Davis)
* T351253: Allow two trailing spaces after ``Bug: Tnnnn`` and ``Change-Id:
  Ixxxx`` trailers for prettier GitLab markdown rendering support. (Bryan
  Davis)

`2.0.0`_ - 2023-11-03
---------------------
* Support "Needed-By:" as a backlink to "Depends-On:" (Daniel Kinzler)
* Alphasort CORRECT_FOOTERS (Sam Reed)
* Convert packaging to hatchling backend (Bryan Davis)
* Introduce RulesMessageValidator (Bryan Davis)
* Add GitLabMessageValidator (Bryan Davis)
* [BREAKING] Add support for checking multiple commits (Bryan Davis)
   * Pre-existing git hook installs will be broken by this change
* Support "Private-Change:" for Puppet Compiler Compiler (John Bond)
* Pre-commit (<https://pre-commit.com/>) plugin support (Bryan Davis)
* [BREAKING] Removed support for self-install as a git hook in favor of
  pre-commit integration.

`1.0.0`_ - 2022-08-13
---------------------
* Improve error reporting (Ahmon Dancy)
* [BREAKING] Drop Python 2.x support (Kunal Mehta)

`0.7.0`_ - 2020-09-08
---------------------
* Accept "Hosts:" footer for puppet-compiler (Antoine Musso)
* Update tests and test configuration (Kunal Mehta)
* Suppress unintentional 'true' print in ``ansi_codes`` (Rafid Aslam)

`0.6.0`_ - 2018-05-15
---------------------
* Use forward slash path separator on Windows (Dalba)
* Add GitHubMessageValidator (Rafid Aslam)
* Add a shebang line to new hooks (Dalba)
* Allow over length subject for reverts (Bryan Davis)
* Allow Depends-On to follow Change-Id (Bryan Davis)
* Add colored error message support (Bryan Davis)

`0.5.2`_ - 2017-11-17
---------------------
* Require sentence case for most footers (Arturo Borrero Gonzalez)

`0.5.1`_ - 2017-11-03
---------------------
* Fix ``commit-message-validator install`` command (Kunal Mehta)

`0.5.0`_ - 2017-11-03
---------------------
* Remove StopIteration for PEP 479 compatibility (Bryan Davis)
* Improved Python 2.x support (Fabian Neundorf)
* Fix test for minimum number of lines (Fabian Neundorf)
* Do not assume last line is always empty (Fabian Neundorf)
* Rewrite procedural functions as class (Fabian Neundorf)
* Normalize BAD_FOOTERS values (Fabian Neundorf)
* Add ``commit-message-validator install`` command (Kunal Mehta)

`0.4.1`_ - 2016-10-17
---------------------
* Build universal wheels (Kunal Mehta)

`0.4.0`_ - 2016-08-22
---------------------
* Add support for "Depends-On" statements (Bryan Davis)
* Allow lines >100 chars if they are URLs (Bryan Davis)
* Validate Gerrit "Change-Id"/"Depends-On" values (Bryan Davis)
* Make rules for footer contents less strict (Bryan Davis)
* Add script to test merged commits in a repository (Kunal Mehta)

`0.3.1`_ - 2016-08-09
---------------------
* Better detection of and handling for merge commits (Kunal Mehta)

`0.3.0`_ - 2016-08-09
---------------------
* Improved Python 3.x support (Kunal Mehta)

`0.2.0`_ - 2016-08-08
---------------------
* Find proper commit when HEAD is a merge commit (Kunal Mehta)
* Improved feedback to user on state of checks (Kunal Mehta)

`0.1.0`_ - 2016-08-08
---------------------
Initial release as Python package forked from the Wikimedia Foundation's
https://gerrit.wikimedia.org/g/integration/config repository. Git history was
not preserved when splitting the code out. This initial code was the result of
collaboration between Bryan Davis and Kunal Mehta. See
https://phabricator.wikimedia.org/T109119 for more details.

* First line <=80 chars
* Second line blank
* No line >100 characters
* "Bug:" is capitalized
* "Bug:" is followed by a space
* Exactly one task id on each "Bug:" line
* No "Task: ", "Fixes: ", "Closes: " lines

.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html
.. _2.2.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v2.1.0...v2.2.0
.. _2.1.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v2.0.0...v2.1.0
.. _2.0.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v1.0.0...v2.0.0
.. _1.0.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.7.0...v1.0.0
.. _0.7.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.6.0...v0.7.0
.. _0.6.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.5.2...v0.6.0
.. _0.5.2: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.5.1...v0.5.2
.. _0.5.1: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.5.0...v0.5.1
.. _0.5.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.4.1...v0.5.0
.. _0.4.1: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.4.0...v0.4.1
.. _0.4.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.3.1...v0.4.0
.. _0.3.1: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.3.0...v0.3.1
.. _0.3.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.2.0...v0.3.0
.. _0.2.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/compare/v0.1.0...v0.2.0
.. _0.1.0: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/commits/v0.1.0/

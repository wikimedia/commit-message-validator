UNRELEASED
----------
* Support "Needed-By:" as a backlink to "Depends-On:" (Daniel Kinzler)
* Alphasort CORRECT_FOOTERS (Sam Reed)
* Convert packaging to hatchling backend (Bryan Davis)
* Introduce RulesMessageValidator (Bryan Davis)
* Add GitLabMessageValidator (Bryan Davis)
* [BREAKING] Add support for checking multiple commits (Bryan Davis)
  * Pre-existing git hook installs will be broken by this change
* Support "Private-Change:" for Puppet Compiler Compiler (John Bond)

1.0.0
-----
* Improve error reporting (Ahmon Dancy)
* [BREAKING] Drop Python 2.x support (Kunal Mehta)

0.7.0
-----
* Accept "Hosts:" footer for puppet-compiler (Antoine Musso)
* Update tests and test configuration (Kunal Mehta)
* Suppress unintentional 'true' print in ``ansi_codes`` (Rafid Aslam)

0.6.0
-----
* Use forward slash path separator on Windows (Dalba)
* Add GitHubMessageValidator (Rafid Aslam)
* Add a shebang line to new hooks (Dalba)
* Allow over length subject for reverts (Bryan Davis)
* Allow Depends-On to follow Change-Id (Bryan Davis)
* Add colored error message support (Bryan Davis)

0.5.2
-----
* Require sentence case for most footers (Arturo Borrero Gonzalez)

0.5.1
-----
* Fix ``commit-message-validator install`` command (Kunal Mehta)

0.5.0
-----
* Remove StopIteration for PEP 479 compatibility (Bryan Davis)
* Improved Python 2.x support (Fabian Neundorf)
* Fix test for minimum number of lines (Fabian Neundorf)
* Do not assume last line is always empty (Fabian Neundorf)
* Rewrite procedural functions as class (Fabian Neundorf)
* Normalize BAD_FOOTERS values (Fabian Neundorf)
* Add ``commit-message-validator install`` command (Kunal Mehta)

0.4.1
-----
* Build universal wheels (Kunal Mehta)

0.4.0
-----
* Add support for "Depends-On" statements (Bryan Davis)
* Allow lines >100 chars if they are URLs (Bryan Davis)
* Validate Gerrit "Change-Id"/"Depends-On" values (Bryan Davis)
* Make rules for footer contents less strict (Bryan Davis)
* Add script to test merged commits in a repository (Kunal Mehta)

0.3.1
-----
* Better detection of and handling for merge commits (Kunal Mehta)

0.3.0
-----
* Improved Python 3.x support (Kunal Mehta)

0.2.0
-----
* Find proper commit when HEAD is a merge commit (Kunal Mehta)
* Improved feedback to user on state of checks (Kunal Mehta)

0.1.0
-----
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

Commit Message Validator
========================

``commit-message-validator`` is a tool that validates git commit messages to
the `Wikimedia commit message guidelines`_.

Please see <https://www.mediawiki.org/wiki/commit-message-validator> for more
details.

Installation
------------

Use ``pip`` to install the latest stable version of
``commit-message-validator``:

.. code-block:: bash

   python3 -m pip install --user --upgrade commit-message-validator


Usage
-----

Install ``commit-message-validator`` as a pre-commit hook for every git repo
you wish to run it on.

.. code-block:: bash

   cd /path/to/git/repository
   ~/.local/bin/commit-message-validator install

Pre-commit
----------

``commit-message-validator`` can be used as a plugin for the `pre-commit`_ git
hooks system. Add the following to your ``.pre-commit-config.yaml``:

.. code-block:: yaml

   -  repo: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator
      rev: # Fill in a tag / sha here (like v2.0.0)
      hooks:
      -  id: commit-message-validator

Then install the pre-commit hook:

.. code-block:: bash

   pre-commit install --hook-type commit-msg

Contributing
------------

See CONTRIBUTING.rst_ for guidelines on contributing to
``commit-message-validator``.

Bug reports
-----------

Please reports bugs and feature requests at
https://phabricator.wikimedia.org/tag/commit-message-validator/.

License
-------

Licensed under the `GPL-2.0-or-later`_ license. See COPYING_ for the full
license.

.. _Wikimedia commit message guidelines: https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines
.. _CONTRIBUTING.rst: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/blob/main/CONTRIBUTING.rst
.. _GPL-2.0-or-later: https://www.gnu.org/licenses/gpl-2.0.html
.. _COPYING: https://gitlab.wikimedia.org/repos/ci-tools/commit-message-validator/-/blob/main/COPYING

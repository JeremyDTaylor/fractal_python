.. highlights:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/JeremyDTaylor/fractal_python/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Fractal Python could always use more documentation, whether as part of the
official Fractal Python docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/JeremyDTaylor/fractal_python/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `fractal_python` for local development:

#. Fork the `fractal_python` repo on GitHub.
#. Clone your fork locally::

    $ git clone git@github.com:your_name_here/fractal_python.git

#. Install pre-commit into your git hooks. `pre-commit <https://pre-commit.com>`_ will now run on every commit::

    $ pre-commit install

#. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv fractal_python
    $ cd fractal_python/
    $ python setup.py develop

#. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

#. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 fractal_python tests
    $ python setup.py test or pytest
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

#. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

#. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.6, 3.7, 3.8, and 3.9. Check
   https://travis-ci.com/JeremyDTaylor/fractal_python/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

Install `pyenv <https://github.com/pyenv/pyenv#installation>`_ to run the tox tests locally::

    $ pyenv local 3.9.2 3.8.8 3.7.10 3.6.13
    $ tox

To run a subset of tests::

    $ pytest tests.banking

To check the code coverage::

    $ coverage run --source=fractal_python setup.py test
    $ coverage report -m

Run black, isort, mypy etc. on everything::

    $ pre-commit run --all-files

Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags

Travis will then deploy to PyPI if tests pass.

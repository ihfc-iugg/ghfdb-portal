from invoke import task


@task
def install(c):
    """
    Install the project dependencies
    """
    print("🚀 Creating virtual environment using pyenv and poetry")
    c.run("poetry install")
    c.run("poetry run pre-commit install")
    c.run("poetry shell")


@task
def check(c):
    """
    Check the consistency of the project using various tools
    """
    print("🚀 Checking Poetry lock file consistency with 'pyproject.toml': Running poetry lock --check")
    c.run("poetry lock --check")

    print("🚀 Linting code: Running pre-commit")
    c.run("poetry run pre-commit run -a")

    print("🚀 Static type checking: Running mypy")
    c.run("poetry run mypy")

    print("🚀 Checking for obsolete dependencies: Running deptry")
    c.run("poetry run deptry .")


@task
def test(c, tox=False):
    """
    Run the test suite
    """
    if tox:
        print("🚀 Testing code: Running pytest with all tests")
        c.run("tox")
    else:
        print("🚀 Testing code: Running pytest")
        c.run("poetry run pytest --cov --cov-config=pyproject.toml --cov-report=html")


@task
def docs(c):
    """
    Build the documentation and open it in the browser
    """
    # c.run("sphinx-apidoc -M -T -o docs/ project/schemas/* **/migrations/* -e --force -d 2")
    # c.run("sphinx-build -E -b html docs docs/_build")
    c.run("docker compose -f local.yml up docs")


@task
def release(c, rule=""):
    """
    Create a new git tag and push it to the remote repository.

    .. note::
        This will create a new tag and push it to the remote repository, which will trigger a new build and deployment of the package to PyPI.

    RULE	    BEFORE	AFTER
    major	    1.3.0	2.0.0
    minor	    2.1.4	2.2.0
    patch	    4.1.1	4.1.2
    premajor	1.0.2	2.0.0a0
    preminor	1.0.2	1.1.0a0
    prepatch	1.0.2	1.0.3a0
    prerelease	1.0.2	1.0.3a0
    prerelease	1.0.3a0	1.0.3a1
    prerelease	1.0.3b0	1.0.3b1
    """
    if rule:
        # bump the current version using the specified rule
        c.run(f"poetry version {rule}")

    # 1. Get the current version number as a variable
    version_short = c.run("poetry version -s", hide=True).stdout.strip()
    version = c.run("poetry version", hide=True).stdout.strip()

    # 2. commit the changes to pyproject.toml
    c.run(f'git commit pyproject.toml -m "bump to v{version_short}"')

    # 3. create a tag and push it to the remote repository
    c.run(f'git tag -a v{version_short} -m "{version}"')
    c.run("git push --tags")
    c.run("git push origin main")


@task
def runserver(c, f="local", build=False):
    """
    Start the development server
    """
    print(f"🚀 Starting the {f} server")
    if build:
        # print("Locking dependencies")
        # c.run("poetry lock")
        print("🚀 Building the images")
    # print(f"docker compose -f {f}.yml up django {'--build' if build else ''} -d")
    c.run(f"docker compose -f {f}.yml up django {'--build' if build else ''} -d")


@task
def reset_db(c):
    """
    Build the documentation and open it in a live browser
    """
    c.run("docker compose -f local.yml run django python manage.py flush")


@task
def run(c, command):
    """
    Start the development server
    """
    c.run(f"docker compose -f local.yml run django {command}")


@task
def dumpdata(c):
    c.run(
        "docker compose -f local.yml run django python manage.py dumpdata users organizations contributors projects"
        " datasets samples core --natural-foreign --natural-primary --output=geoluminate.json.gz"
    )


@task
def loaddata(c):
    c.run("docker compose -f local.yml run django python manage.py loaddata core --app geoluminate")


@task
def create_fixtures(c, users=75, orgs=25, projects=12):
    """
    Build the documentation and open it in a live browser
    """
    c.run(
        f"docker compose -f local.yml run django python manage.py create_fixtures --users {users} --orgs {orgs} --projects {projects}"
    )

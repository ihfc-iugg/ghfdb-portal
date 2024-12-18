import datetime

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
    Release a new version of the app using year.release-number versioning.
    """
    # if rule:
    #     # bump the current version using the specified rule
    #     c.run(f"poetry version {rule}")

    # # 1. Get the current version number as a variable
    # version_short = c.run("poetry version -s", hide=True).stdout.strip()
    # version = c.run("poetry version", hide=True).stdout.strip()

    # # 2. commit the changes to pyproject.toml
    # c.run(f'git commit pyproject.toml -m "bump to v{version_short}"')

    # # 3. create a tag and push it to the remote repository
    # c.run(f'git tag -a v{version_short} -m "{version}"')
    # c.run("git push --tags")
    # c.run("git push origin main")

    # # 1. Bump and commit the version
    # vnum = c.run(f"poetry version {rule} -s", hide=True).stdout.strip()
    # c.run(f'git commit pyproject.toml -m "bump version v{vnum}"')

    # if rule in ["major", "minor"]:
    #     # 3. create a tag and push it to the remote repository
    #     c.run(f'git tag -a v{vnum} -m "{vnum}"')
    #     c.run("git push --tags")

    # 1. Determine the current year
    current_year = datetime.datetime.now().year

    # 2. Get the latest tag to find the current release number
    # result = c.run(
    #     f"git tag --list 'v{current_year}.*' --sort=-v:refname",
    #     hide=True,
    #     warn=True,
    # )
    # tags = result.stdout.strip().splitlines()
    # version = c.run("poetry version", hide=True).stdout.strip()
    year, num = c.run("poetry version -s", hide=True).stdout.strip().split(".")

    year = int(year)
    num = int(num)

    # # 3. Form the new version string
    version = f"{current_year}.1" if year != current_year else f"{year}.{num + 1}"

    # # 4. Update the version in pyproject.toml
    c.run(f"poetry version {version}")

    # # 5. Commit the change
    c.run(f'git commit pyproject.toml -m "release v{version}"')

    # # 6. Create a tag and push it
    c.run(f'git tag -a v{version} -m "Release {version}"')
    c.run("git push --tags")
    c.run("git push origin main")


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


@task
def savedemo(c):
    """Save the initial data for the core geoluminate app"""
    c.run(
        " ".join(
            [
                "docker compose run",
                "django python -Xutf8 manage.py dumpdata",
                "--natural-foreign",
                "--natural-primary",
                # "-e users.User",
                "-e admin.LogEntry",
                "-e contenttypes",
                "-e auth.Permission",
                "-e sessions",
                "-o project/fixtures/project.json.bz2",
            ]
        )
    )


@task
def update_deps(c):
    """
    Update the project dependencies
    """
    packages = [
        "django-easy-icons",
        "django-literature",
        "django-jsonfield-toolkit",
        "django-polymorphic-treebeard",
        "django-account-management",
        "geoluminate-docs",
        "django-research-vocabs",
        "django-setup-tools",
        "django-flex-menus",
    ]

    c.run(f"poetry update {' '.join(packages)}")

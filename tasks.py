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
def docs(c, live=False):
    """
    Build the documentation
    """
    if live:
        c.run(
            "sphinx-autobuild -b html --watch docs -c docs docs docs/_build/html --ignore docs/data_models/* --open-browser --port 5000"
        )
    else:
        c.run("sphinx-build -E -b html docs docs/_build")


@task(help={"overwrite": "Re-release the current version (overwrite tag if needed)"})
def release(c, overwrite=False):
    """
    Release a new version of the app using year.release-number versioning.
    """
    if overwrite:
        version = c.run("poetry version -s", hide=True).stdout.strip()
        print(f"Overwriting release {version}")
    else:
        # 1. Determine the current year
        current_year = datetime.datetime.now().year

        # 2. Get the current version
        year, num = c.run("poetry version -s", hide=True).stdout.strip().split(".")
        year = int(year)
        num = int(num)

        # 3. Form the new version string
        version = f"{current_year}.1" if year != current_year else f"{year}.{num + 1}"

        # 4. Update the version in pyproject.toml
        c.run(f"poetry version {version}")

        # 5. Commit the change
        c.run(f'git commit pyproject.toml -m "release v{version}"')

    # 6. Delete the existing tag if overwriting
    if overwrite:
        c.run(f"git tag -d v{version}", warn=True)
        c.run(f"git push --delete origin v{version}", warn=True)

    # 7. Create a tag and push it
    c.run(f'git tag -a v{version} -m "Release {version}"')
    c.run("git push --tags")
    c.run("git push origin main")


@task
def dumpdata(c):
    c.run(
        "docker compose -f local.yml run django python manage.py dumpdata users organizations contributors projects"
        " datasets samples core --natural-foreign --natural-primary --output=fairdm.json.gz"
    )


@task
def loaddata(c):
    c.run("docker compose -f local.yml run django python manage.py loaddata core --app fairdm")


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
    """Save the initial data for the core fairdm app"""
    c.run(
        " ".join(
            [
                "python -Xutf8 manage.py dumpdata",
                "--natural-foreign",
                "--natural-primary",
                "-e users.User",
                "-e admin.LogEntry",
                "-e contenttypes",
                "-e auth.Permission",
                "-e sessions",
                "-o fixtures/demo.json",
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
        "fairdm-docs",
        "django-research-vocabs",
        "django-setup-tools",
        "django-flex-menus",
    ]

    c.run(f"poetry update {' '.join(packages)}")


@task
def build_image(c):
    c.run("docker build -t ghcr.io/ihfc-iugg/ghfd-portal .")

# Getting Started

This guide outlines the steps to contribute to this application. By following these instructions, you can fork the repository, set up a virtual environment, make changes, write tests, and submit a pull request to the main repository.

## Prerequisites

```{important}
Please review the contributor [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) before contributing to this project.
```

Before you begin, ensure that you have the following installed on your local machine:

- [Git](https://git-scm.com/downloads)
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/get-docker/) with Compose, for the PostGIS database
- The GDAL, GEOS and PROJ libraries, to run Django on your own machine rather than in Docker. On Debian and Ubuntu, `apt install gdal-bin` installs all three. Where they are not on the system library path, set `GDAL_LIBRARY_PATH` and `GEOS_LIBRARY_PATH` to the library files.

## Step 1: Fork the Repository and Clone it to Your Local Machine

1. Click on the "Fork" button at the top right corner of the [repository page](https://github.com/ihfc-iugg/ghfdb-portal).
2. After forking, you'll be redirected to your forked repository. Copy the URL of your forked repository.
3. Open a terminal or command prompt.
4. Change to the directory where you want to clone the repository.
5. Run the following command to clone the repository:

   ```shell
   git clone <forked_repository_url>
   ```

   Replace `<forked_repository_url>` with the URL of your forked repository.

## Step 2: Set up a Virtual Environment and Install Project Dependencies

1. Change to the cloned repository's directory:

   ```shell
   cd ghfdb-portal
   ```

2. Run the following command to set up a virtual environment using uv:

   ```shell
   uv sync
   ```

   This command will create a new virtual environment and install the project's dependencies.

## Step 2a: Start the Database

The portal runs on PostgreSQL with the PostGIS extension, in development as in production. The repository's `docker-compose.yml` provides it.

- To run everything in Docker, start the whole stack:

  ```shell
  docker compose up
  ```

  This starts PostGIS, Redis, a Celery worker and the development server, which applies the migrations to an empty database and serves the site on <http://localhost:8000>. The source is mounted into the container, so edits reload.

- To run Django and the tests on your own machine, start the databases alone:

  ```shell
  docker compose up -d postgres redis
  uv run python manage.py migrate
  uv run python manage.py runserver
  ```

  `stack.development.env` points Django at the database on `localhost:5432`. A `POSTGRES_*` variable already set in your environment takes precedence over the file.

  To fill an empty database with demo datasets, follow [](demo-data.md).

## Step 3: Create a New Branch for Your Contribution

1. Run the following command to create a new branch:

   ```shell
   git checkout -b <branch_name>
   ```

   Replace `<branch_name>` with a descriptive name that reflects the nature of your changes.

## Step 4: Make Your Changes

1. Use your favorite code editor to make the desired changes to the project's code.
2. Follow the coding style and best practices of the project to maintain consistency.

## Step 5: Write Tests for Your Changes

1. Ensure that the project has a testing framework in place.
2. Write tests to cover your changes, ensuring that they pass successfully.
3. With the database running (Step 2a), run the tests:

   ```shell
   uv run pytest
   ```

   The suite runs against PostGIS. `tests/README.md` describes how it is laid out and how to run part of it.

## Step 6: Commit Your Changes

1. Run the following command to stage your changes for commit:

   ```shell
   git add .
   ```

   This command stages all modified files for commit. If you only want to stage specific files, replace `.` with the file paths.

2. Commit your changes with a clear and concise commit message:

   ```shell
   git commit -m "Your commit message"
   ```

   Replace `"Your commit message"` with a descriptive message that explains the purpose of your changes.

## Step 7: Push Your Branch to Your Forked Repository

1. Run the following command to push your branch to your forked repository:

   ```shell
   git push origin <branch_name>
   ```

   Replace `<branch_name>` with the name of the branch you created in Step 3.

## Step 8: Submit a Pull Request

1. Visit your forked repository on GitHub.
2. Click on the "Compare & pull request" button next to your pushed branch.
3. Provide a detailed description of your changes and the problem they solve.
4. Review your changes and ensure that all necessary information is included.
5. Click on the "Create pull request" button to submit your pull request.

Congratulations! You've successfully contributed to the main repository by following these steps. Your pull request will be reviewed by the project maintainers, who may provide feedback or request further changes.

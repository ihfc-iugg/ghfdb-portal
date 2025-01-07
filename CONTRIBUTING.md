# Contributing

```{attention}
Development of this application is currently led by the [World Heat Flow Database Project](http://heatflow.world). Contributions from the community in the form of bug fixes are welcome and encouraged. However, new features should be discussed with the project maintainers before development begins.
```

This guide outlines the steps to contribute to this application. By following these instructions, you can fork the repository, set up a virtual environment, make changes, write tests, and submit a pull request to the main repository.

## Prerequisites

```{important}
Please review the contributor [Code of Conduct](code_of_conduct.md) before contributing to this project.
```

Before you begin, ensure that you have the following installed on your local machine:

- [Git](https://git-scm.com/downloads)
- [Docker](https://docs.docker.com/get-docker/
- [Python Poetry](https://python-poetry.org/docs/) (version 1.1.0 or higher)

## Step 1: Fork the Repository and Clone it to Your Local Machine

1. Click on the "Fork" button at the top right corner of the [repository page](https://github.com/WorldHeatFlowDatabase/world-heat-flow-database).
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
   cd world-heat-flow-database
   ```

2. Run the following command to set up a virtual environment using Poetry:

   ```shell
   poetry install
   ```

   This command will create a new virtual environment and install the project's dependencies.

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
3. Run the tests using the appropriate command (often provided in the project's documentation).

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

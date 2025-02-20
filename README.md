# Heatflow.world

[![Github Build](https://github.com/ihfc-iugg/ghfdb-portal/actions/workflows/build.yml/badge.svg)](https://github.com/ihfc-iugg/ghfdb-portal/actions/workflows/build.yml)
[![Github Docs](https://github.com/ihfc-iugg/ghfdb-portal/actions/workflows/docs.yml/badge.svg)](https://github.com/ihfc-iugg/ghfdb-portal/actions/workflows/docs.yml)
[![Github Docs](https://github.com/ihfc-iugg/ghfdb-portal/actions/workflows/docker-build-and-publish.yml/badge.svg)](https://github.com/ihfc-iugg/ghfdb-portal/actions/workflows/docker-build-and-publish.yml)
![GitHub](https://img.shields.io/github/license/ihfc-iugg/ghfdb-portal)
![GitHub last commit](https://img.shields.io/github/last-commit/ihfc-iugg/ghfdb-portal)

This repository hosts the codebase of the Heatflow.world portal. The portal is a web application that provides access to the Global Heat Flow Database (GHFDB). The GHFDB is a collection of heat flow measurements from around the world. The portal allows users to search, filter, and download data from the GHFDB as well as individual publications. The portal is built using the Django web framework and the official version is hosted at by GFZ Potsdam, Germany.

To learn more, see the full documentation at [https://heatflowworld.readthedocs.io/](https://heatflowworld.readthedocs.io/)

## Acknowledgements

This codebase is maintained by the [German Research Centre for Geosciences (GFZ)](https://www.gfz-potsdam.de/en/) as part of the [World Heat Flow Database Project](https://www.heatflow.world). This project is funded by the [Deutsche Forschungsgemeinschaft (DFG)](https://www.dfg.de) under the project number [491795283](https://gepris-extern.dfg.de/gepris/projekt/491795283).

We extend our gratitude to all individuals, organizations, and institutions who have contributed to and supported this project. For a complete list of contributors, see [CONTRIBUTORS.md](./CONTRIBUTORS.md).

## Supporting Organizations

[![World Heat Flow Database Project](./assets/img/brand/logo.png)](https://www.heatflow.world)
[![Deutsche Forschungsgemeinschaft](./assets/img/brand/DFG.gif)](https://www.dfg.de)
[![GFZ](./assets/img/brand/GFZ_logo.png)](https://www.gfz-potsdam.de)
[![TUD](./assets/img/brand/TUD_Logo_HKS41_57.png)](https://tu-dresden.de/)

## Fork

[Fork according to GitHub tutorial](https://docs.github.com/de/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#cloning-your-forked-repository)

### Setup Portel

#### Clean up heat_flow/migrations

In heat_flow/migrations delete all files excep _init_.py

#### Setup project

```bash
python manage.py setup
```

### Actions for Portal and Docs

#### Run Docs

```bash
cd ProjectDir/
poetry shell
invoke docs --live
```

[Demo](http://127.0.0.1:5000/mapping/index.html)

#### Run Portel

```bash
python manage.py runserver
```

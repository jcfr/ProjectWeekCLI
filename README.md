# ProjectWeek CLI

CLI for processing project week mardown-based documents.

_Project created in the context of the following discussion. See https://discourse.slicer.org/t/cli-for-processing-markdown-based-project-pages/27447._

## Download project week files

```
cd $HOME/Projects
git clone --depth=1 --branch master https://github.com/NA-MIC/ProjectWeek.git
```

## Install the CLI

```
cd $HOME/Projects
git clone https://github.com/jcfr/ProjectWeekCLI.git
```


## Running the CLI

```
project_week=$HOME/Projects/ProjectWeek/PW38_2023_GranCanaria
project_week_cli=$HOME/Projects/ProjectWeekCLI/project_week_cli.py

(\
  cd ${project_week}/Projects/;  \
  fd README.md -a -exec python3 ${project_week_cli} {} \
)
```


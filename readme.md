# Spider web

## Development

There we use the django framework to build the web for all-stack. Here is the development start cmd:

```shell
cd spider_project
python manage.py runserver 0.0.0.0:80
```

> This output the development server on the 80 port. is cause much security issue, so we should not use this in production.

production start cmd:

```shell
cd spider_project
nohup ../.venv/bin/python3 manage.py runserver 0.0.0.0:80 &
```

TODO: the production start cmd.

## Apply Migrations

Create and apply the initial migrations for your models, i.e. here use sqlite3 as the database. Detail run command:

```shell
python manage.py makemigrations 
python manage.py migrate
```

## Architecture Change Reason

Before the web version, the desktop version had several issues:

- **Version Updates:** Updating the version was not easy. Users needed to download and install the new version manually.
- **Error Logs:** Retrieving error logs was cumbersome. Users had to send the log files to us.
- **Network Issues:** The spider required an overseas network to fetch data. Some users had unstable networks, so we switched to using an overseas server to get the data.

Based on these issues, we decided to build a web version to provide the service.

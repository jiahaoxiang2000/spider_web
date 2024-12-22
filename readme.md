# Spider web

## Development

There we use the django framework to build the web for all-stack. Here is the development start cmd:

## Will DO

- [x] the account keep live function on all day
- [x] the spider task
  - [x] the spider logic, need control the spider speed
  - [x] the timing run on every day 00:30

## Installation And Running

```bash
pip install -r ../requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Deployment

here we use the docker python image to deploy, there is the start cmd:

```bash
pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000 
```

## Apply Migrations

Create and apply the initial migrations for your models, i.e. here use sqlite3 as the database. Detail run command:

## Architecture Change Reason

Before the web version, the desktop version had several issues:

- **Version Updates:** Updating the version was not easy. Users needed to download and install the new version manually.
- **Error Logs:** Retrieving error logs was cumbersome. Users had to send the log files to us.
- **Network Issues:** The spider required an overseas network to fetch data. Some users had unstable networks, so we switched to using an overseas server to get the data.

Based on these issues, we decided to build a web version to provide the service.

# AnimeGAN

### Datasets
[dateset of Arcane faces](https://www.kaggle.com/datasets/artermiloff/arcanefaces)\
[dateset of normal human faces](https://www.kaggle.com/datasets/ashwingupta3012/human-faces)

### Usage

Build:
`docker build -t <tag> .`\
Run: 
`docker run -e TOKEN=<token> -e DATABASE_URL=<database_url> -d <tag>`,
where `tag` is tag of docker image, `token` is telegram bot token, `database_url` is postgres url in form `postgresql://<user>:<password>@<host>:<port>/<database>`

Or you can use .env file: `docker run --env-file <file_name> -d <tag>`, and file contains `TOKEN` and `DATABASE_URL`
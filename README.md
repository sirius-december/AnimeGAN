# AnimeGAN

### Datasets
[dateset of Arcane faces](https://www.kaggle.com/datasets/artermiloff/arcanefaces)\
[dateset of normal human faces](https://www.kaggle.com/datasets/ashwingupta3012/human-faces)

### Usage

Build:
`docker build -t <tag> .`, where `tag` is desired tag of docker image\

While building there should be file folder keys in root directory and file `keys/datasphere-key.json` with keys from service account which has access to Datasphere.

Run:`docker run -e env1=<env1> -e env2=<env2> -e ... -d <tag>`\
Or via .env file: `docker run --env-file <file_name> -d <tag>`


Required Env variables:
- `TOKEN` – telegram bot token
- `DATABASE_URL` – url to connect to postgres database. Should be in form `postgresql://<user>:<password>@<host>:<port>/<database>`
- `AWS_ACCESS_KEY_ID` – AWS access key ID
- `AWS_SECRET_ACCESS_KEY` – AWS secret access key
- `AWS_DEFAULT_REGION` – AWS region
- `AWS_ENDPOINT_URL` – AWS endpoint URL
- `YANDEX_OAUTH` – Yandex OAUTH token for account with access to datasphere
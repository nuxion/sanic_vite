# Sanic Vite

:construction: Work in progress :construction:

An opinated template for Sanic to be used as an api server or like a traditional web server with vite integration. 

It provides: 

1. vite integration, svelte by default but could be changed
2. static helper for jinja templates like django
3. collectstatic command which collects vite assets and jinja used assets
4. api service endpoints with openapi/swagger documentation

## Folder structure

`changeme`: main python package could be changed with the `rename.sh` script
    `changeme/server.py`: Sanic's server factory
    `chageme/services/`: any module which ends with **_bp** will be included as route. This is for API services.
    `chageme/pages/`: as services, any file which ends with **_bp** will be included. This is for traditional web pages rendering. 
    
`templates`: Where templates and dynamic js sites goes.

`public`: images and files that doesn't change like robots.txt, this dir is shared by vite and sanic. 

## How to use

This repo could be used with [degit tool](https://github.com/Rich-Harris/degit):

```
degit https://github.com/nuxion/python_template
```

Or more conventionally:

```
git clone --depth 1 https://github.com/nuxion/python_template <your_project>
cd <your_project>
rm -Rf .git 
git init .
```

Change files name using `rename.sh` script (look into it first!)

```
./rename.sh new_name
```

After that, if you are using poetry:

```
poetry install
```

If not, then (create a virtualenv first): 
```
python3 setup.py install
```

Running webserver:

```
sbuilder web --vite-server
```

Collecting assets:

```
sbuilder collectstatic outputdir --vite-build
```

## Vite configuration

The `changeme.types.config.Settings` class has configurations options for vite that should be in sync with the `vite.config.js` file. Next, some descriptions:

- VITE_STATIC_URL_PATH: path where the asset is used in the javascript applications
- VITE_STATIC_DIR: Where the javascript assets are in the local pc. 
- VITE_OUTPUT_DIR: Where vite will put the built files: `build.outDir`
- VITE_DEV_SERVER: Address and port where vite server is running. *http://localhost:3000* by default.
- VITE_DEV_MODE: If dev mode or not (should be managed by env)
- VITE_BASE: path in the dev-server, `base` param in the vite file. 



## Possible roadmap

- [ ] Auth 
- [ ] SQLAlchemy & Alembic
- [ ] more documentation about how to use
- [ ] Tailwindcss ?
- [ ] CI/CD: dockerfile, Makefile, pylint, black ...
- [ ] pytest, factoryboy, async support
- [ ] Markdown support


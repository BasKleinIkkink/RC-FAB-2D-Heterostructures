# How To Use
This folder contains all the documents needed to create documentation using Sphinx with
numpy style docstrings (using napoleon).

## Creating function files
With the current config numpy docstrings wont be documented correctly, for this to work
you first have to run the following line from within this folder.

```bash
sphinx-apidoc -o apidoc_generated ../package_name
```

This only has to be done once at the beginning of the project. When this is done
again it will overwrite the existing files.

## Updating/creating the docs
As this folder is only set up for building html docs use the following line to update.

```bash
make html
```

The files will be put in the build folder under the type that was created.
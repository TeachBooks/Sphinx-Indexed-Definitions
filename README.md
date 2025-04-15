# Sphinx Indexed Definitions

## Introduction

This Sphinx extension provides an easy way to add entries to a genreated index based on **strong**, *emphasized* and/or `literal` terms used within `prf:definition` admonitions and the title of the adminition.

## What does it do?

If you code includes an admonition with the source code

```md
:::{prf:definition} Lorem
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse **Pharetra**, ex ut commodo varius,
est justo vestibulum nunc, *(id) dignissim* lorem nibh in mauris. Duis varius lorem et neque posuere,
ac elementum eros consequat. Maecenas sed risus suscipit, **fermentum Kelvin** quam vitae, consectetur
augue. Maecenas aliquam leo vitae velit interdum efficitur.
:::
```

this extension, once loaded, will add (with default settings) the terms Lorem, **pharetra**, *id dignissim*, *dignissim* and **fermentum Kelvin** to the generated index.

## Installation
To use this extenstion, follow these steps (be aware, more steps then usual):

**Step 1: Install the Package**

Install the module `sphinx-indexed-definitions` package using `pip`:
```
pip install git+https://github.com/TeachBooks/Sphinx-Indexed-Definitions.git
```
    
**Step 2: Add to `requirements.txt`**

Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
git+https://github.com/TeachBooks/Sphinx-Indexed-Definitions.git
```

**Step 3: Enable in `_config.yml`**

In your `_config.yml` file, add the extension to the list of extra Sphinx extensions (**important**: underscore, not dash this time):
```
sphinx: 
    extra_extensions:
        .
        .
        .
        - sphinx_indexed_definitions
        .
        .
        .
```

**Step 4: Add the general index to ToC**

To do this, if you have not done this, please follow the instructions at [Add the general index to your table of contents](https://jupyterbook.org/en/stable/content/content-blocks.html#add-the-general-index-to-your-table-of-contents).

## Configuration

The extension provides several configuration values, which can be added to `_config.yml` if the default value should be changed:

```yaml
sphinx: 
    config:
        -
        -
        -
        sphinx_indexed_defs_indexed_nodes:     ['strong','emphasis'] # default value
        sphinx_indexed_defs_skip_indices:      []                    # default value
        sphinx_indexed_defs_lowercase_indices: true                  # default value
        sphinx_indexed_defs_index_titles:      true                  # default value
        sphinx_indexed_defs_capital_words:     []                    # default value
        sphinx_indexed_defs_remove_brackets:   true                  # default value
        sphinx_indexed_defs_force_main:        true                  # default value
        -
        -
        -
```
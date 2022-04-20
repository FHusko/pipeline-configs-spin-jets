Pipeline Configs
================

This repository stores the pipeline configs that are used for
the various [SWIFT](http://swift.dur.ac.uk) simulations
using the [pipeline](http://github.com/swiftsim/pipeline).

The only required setup to use the configs is to format the
observational data, which is performed using the submodule:

```bash
git submodule update --init --recursive
cd observational_data
./convert.py [--nproc <NUMBER OF PARALLEL PROCESSES>]
cd ..
```

That should be everything you need to get going, as well as
the documentation available in the ``pipeline`` repository.

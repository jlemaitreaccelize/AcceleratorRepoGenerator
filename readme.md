# Accelerator Repository Generator

Generates or updates following files for accelerator repository based on template:
* `readme.md`
* `run_example.py`
* `LICENSE`
. `.gitignore`

## Getting started

### Generates new repository
* Create Git repository for the Accelerator.
* Copy `accelerator_def.xml` from current repository to `.resources/accelerator_def.xml` in accelerator repository.
* Edit and complete `.resources/accelerator_def.xml` using accelerator information.
* run `./generator.py --path AcceleratorRepositoryPath`.
* Add extra files to accelerator repository (samples, ...).

### Update repository
* (Optional) Edit `.resources/accelerator_def.xml` using accelerator information.
* run `./generator.py --path AcceleratorRepositoryPath`.

# Microbial-OMICs
This repository holds the metadata schemes for the DZIF microbial OMICs database. The schemes are located in `schemes/metaDZIF.yaml`. They are implemented in [LinkML](https://linkml.io/) and are derived from the [NFDI4Microbiota](https://nfdi4microbiota.de/) [metadata standards](https://gitfront.io/r/MDS-Majid/wh11wCd2JZQM/NFDI4Microbiota-MetadataStandards/). So far NGS-based schemes are implemented. Mass-spec related schemes should be released mid of 2024.

To insert ontologies as controlled vocabularies and build the DZIF DataHarmonizer, a fork of the original [DataHarmonizer](https://github.com/cidgoh/DataHarmonizer), run the script `DataHarmonizerBuilder.py` in the `src` folder after creating a [conda](https://anaconda.org) environment from the `environment.yaml` with the flag `--repo <name of this repository/folder>`. If you are unfamiliar with conda please refer to their [documentation](https://docs.anaconda.com/free/anaconda/install/) for installation.
<!--- TODO: Insert link to repo of DZIF DataHarmonizer --->
For setup and activation of the environment:
1. `conda env create -f environment.yml`
2. `conda activate Microbial-OMICs`

After setup and activation of the created conda environment, run this command from the repository folder:

```bash
python3 src/DataHarmonizerBuilder.py --repo <name of this repo/folder>
```

`<name of this repo/folder>` is the name of the folder this `README.md` is located in.

The built DZIF DataHarmonizer will be located in the folder `DZIFDataHarmonizer` and the schemes can be found in the `final` folder. 

The used ontologies can be updated to a newer version by editing the `config/config.yaml` file. To start with this, first locate the newest version of the specific ontology using the [Ontology Lookup Service](https://www.ebi.ac.uk/ols4/) (for updating the [ROR](https://ror.org/) file for organizations in the `collected by` field go to the respective [zenodo](https://zenodo.org/doi/10.5281/zenodo.6347574) repository) and then insert this information into the `config.yaml` and push it to the github repository master branch. This should be accompanied by also making a new release of the DZIF DataHarmonizer with an updated version number using [semantic versioning](https://semver.org/). The version of the metadata scheme has to be updated in the `metaDZIF.yaml` file (changing the `version: 1.0.0` to `version: 1.1.0`, for example) located in the `schemes` folder.

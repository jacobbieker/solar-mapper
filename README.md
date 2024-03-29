<div align="center">

# Global Solar Panel Mapper

<a href="https://pytorch.org/get-started/locally/"><img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white"></a>
<a href="https://pytorchlightning.ai/"><img alt="Lightning" src="https://img.shields.io/badge/-Lightning-792ee5?logo=pytorchlightning&logoColor=white"></a>
<a href="https://hydra.cc/"><img alt="Config: Hydra" src="https://img.shields.io/badge/Config-Hydra-89b8cd"></a>

</div>

## Description

This repo attempts to continue and extend [this work](https://github.com/Lkruitwagen/solar-pv-global-inventory) on mapping global solar panel locations, with creating updated maps of their locations since the end of the data in that paper to now on a continuous basis. The Solar PV Inventory used Sentinel-2 data as well as high-resolution satellite imagery to detect solar plants and panels. To try to eliminate the need for expensive high resolution imagery, this project uses the [WorldStrat](https://worldstrat.github.io/) model for super-resolution of Sentinel-2 imagery instead. This project would most likely run on Microsoft's [Planetary Computer](https://planetarycomputer.microsoft.com/catalog) as it already has the Sentinel-2 data with the STAC spec to easily query and use the imagery.

Another paper on the subject, with an accompanying dataset is [this one](https://www.mdpi.com/2072-4292/15/1/210).

## How to run

Install dependencies

```bash
# clone project
git clone https://github.com/YourGithubName/your-repo-name
cd your-repo-name

# [OPTIONAL] create conda environment
conda create -n myenv python=3.9
conda activate myenv

# install pytorch according to instructions
# https://pytorch.org/get-started/

# install requirements
pip install -r requirements.txt
```

Train model with default configuration

```bash
# train on CPU
python src/train.py trainer=cpu

# train on GPU
python src/train.py trainer=gpu
```

Train model with chosen experiment configuration from [configs/experiment/](configs/experiment/)

```bash
python src/train.py experiment=experiment_name.yaml
```

You can override any parameter from command line like this

```bash
python src/train.py trainer.max_epochs=20 datamodule.batch_size=64
```

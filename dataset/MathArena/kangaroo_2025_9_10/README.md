---
dataset_info:
  features:
  - name: problem_idx
    dtype: int64
  - name: answer
    dtype: string
  - name: image
    dtype: image
  splits:
  - name: train
    num_bytes: 2093601.0
    num_examples: 30
  download_size: 2091510
  dataset_size: 2093601.0
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*

license: cc-by-nc-sa-4.0
language:
- en
pretty_name: Kangaroo 2025 9-10
size_categories:
- n<1K
---

### Homepage and repository

- **Homepage:** [https://matharena.ai/](https://matharena.ai/)
- **Repository:** [https://github.com/eth-sri/matharena](https://github.com/eth-sri/matharena)

### Dataset Summary

This dataset contains the questions from Kangaroo 2025 9-10 used for the MathArena Leaderboard.

### Data Fields

Below one can find the description of each field in the dataset.

- `problem_idx` (int): Index of the problem in the competition
- `image` (str): Full problem statement as an image
- `answer` (str): Ground-truth answer to the question. All None for Project Euler.

### Source Data

The original questions were sourced from the Albanian Kangaroo 2025. Questions were extracted, translated, and screenshotted.

### Licensing Information

This dataset is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). Please abide by the license when using the provided data.

### Citation Information

```
@misc{balunovic_srimatharena_2025,
  title = {MathArena: Evaluating LLMs on Uncontaminated Math Competitions},
  author = {Mislav Balunović and Jasper Dekoninck and Ivo Petrov and Nikola Jovanović and Martin Vechev},
  copyright = {MIT},
  url = {https://matharena.ai/},
  publisher = {SRI Lab, ETH Zurich},
  month = feb,
  year = {2025},
}
```

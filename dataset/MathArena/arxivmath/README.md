---
dataset_info:
  features:
  - name: problem_idx
    dtype: int64
  - name: answer
    dtype: string
  - name: problem_type
    list: string
  - name: source
    dtype: float64
  - name: problem
    dtype: string
  - name: competition
    dtype: string
  splits:
  - name: train
    num_bytes: 61958
    num_examples: 103
  download_size: 38192
  dataset_size: 61958
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
license: cc-by-sa-4.0
language:
- en
pretty_name: ArXivMath
size_categories:
- n<1K
---

### Homepage and repository

- **Homepage:** [https://matharena.ai/](https://matharena.ai/)
- **Repository:** [https://github.com/eth-sri/matharena](https://github.com/eth-sri/matharena)

### Dataset Summary

This dataset contains the questions from ArXivMath used for the MathArena Leaderboard

### Data Fields

Below one can find the description of each field in the dataset.

- `problem_idx` (int): Index of the problem in the competition
- `problem` (str): Full problem statement
- `answer` (str): Ground-truth answer to the question
- `problem_type` (sequence[string]): Type of the problem, either "Combinatorics", "Number Theory", "Algebra", "Geometry". One problem can have several types.

### Licensing Information

This dataset is licensed under the Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). Please abide by the license when using the provided data.

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


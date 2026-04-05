---
dataset_info:
  features:
  - name: problem_idx
    dtype: string
  - name: problem
    dtype: string
  - name: points
    dtype: int64
  - name: grading_scheme
    list:
    - name: desc
      dtype: string
    - name: points
      dtype: int64
    - name: title
      dtype: string
  - name: sample_solution
    dtype: string
  - name: sample_grading
    dtype: string
  splits:
  - name: train
    num_bytes: 22010
    num_examples: 6
  download_size: 31598
  dataset_size: 22010
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
license: cc-by-nc-sa-4.0
language:
- en
pretty_name: USAMO 2025
size_categories:
- n<1K
---

### Homepage and repository

- **Homepage:** [https://matharena.ai/](https://matharena.ai/)
- **Repository:** [https://github.com/eth-sri/matharena](https://github.com/eth-sri/matharena)

### Dataset Summary

This dataset contains the questions from USAMO 2025 used for the MathArena Leaderboard

### Data Fields

Below one can find the description of each field in the dataset.

- `problem_idx` (int): Index of the problem in the competition
- `problem` (str): Full problem statement
- `points` (str): Number of points that can be earned for the question.
- `sample_solution` (str): Sample solution that would obtain a perfect score.
- `sample_grading` (str): An example of how a graded solution can look like. The JSON format follows the outline as described in our GitHub repository.
- `grading_scheme` (list[dict]): A list of dictionaries, each of which indicates a specific part of the proof for which points can be obtained. Each dictionary has the following keys:
   - `title` (str): Title associated with this part of the scheme
   - `desc` (str): Description of this part of the grading scheme
   - `points` (str): Number of points that can be obtained for this part of the proof

### Source Data

The original questions were sourced from the USAMO 2025 competition. Questions were extracted, converted to LaTeX and verified.

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


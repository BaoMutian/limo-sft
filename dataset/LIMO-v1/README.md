---
language:
- en
size_categories:
- n<1K
license: apache-2.0
---
Dataset for [LIMO: Less is More for Reasoning](https://github.com/GAIR-NLP/LIMO)

## Usage
```python
from datasets import load_dataset
dataset = load_dataset("GAIR/LIMO", split="train")
```

## Citation

If you find our dataset useful, please cite:
```
@misc{ye2025limoreasoning,
      title={LIMO: Less is More for Reasoning}, 
      author={Yixin Ye and Zhen Huang and Yang Xiao and Ethan Chern and Shijie Xia and Pengfei Liu},
      year={2025},
      eprint={2502.03387},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.03387}, 
}
```
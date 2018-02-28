import logging
import logging.config

import random
import torch

logger = logging.getLogger(__name__)


def resplit_datasets(dataset, other_dataset, random_seed=None, cut=None):
    """ Deterministic shuffle and split algorithm.

    Given the same two datasets and the same `random_seed`, the split happens the same exact way
    every call.

    Args:
        dataset (lib.datasets.Dataset)
        other_dataset (lib.datasets.Dataset)
        random_seed (int, optional)
        cut (float, optional): float between 0 and 1 to cut the dataset; otherwise, the same
            proportions are kept.
    Returns:
        dataset (lib.datasets.Dataset)
        other_dataset (lib.datasets.Dataset)
    """
    # Prevent circular dependency
    from torchnlp.datasets import Dataset

    concat = dataset.rows + other_dataset.rows
    # Reference:
    # https://stackoverflow.com/questions/19306976/python-shuffling-with-a-parameter-to-get-the-same-result
    # NOTE: Shuffle the same way every call of `shuffle_datasets` where the `random_seed` is given
    random.Random(random_seed).shuffle(concat)
    if cut is None:
        return Dataset(concat[:len(dataset)]), Dataset(concat[len(dataset):])
    else:
        cut = max(min(round(len(concat) * cut), len(concat)), 0)
        return Dataset(concat[:cut]), Dataset(concat[cut:])


def torch_equals_ignore_index(tensor, tensor_other, ignore_index=None):
    """
    Compute torch.equals with the optional mask parameter.

    Args:
        ignore_index (int, optional): specifies a tensor1 index that is ignored
    Returns:
        (bool) iff target and prediction are equal
    """
    if ignore_index is not None:
        assert tensor.size() == tensor_other.size()
        mask_arr = tensor.ne(ignore_index)
        tensor = tensor.masked_select(mask_arr)
        tensor_other = tensor_other.masked_select(mask_arr)

    return torch.equal(tensor, tensor_other)


def reporthook(t):
    """https://github.com/tqdm/tqdm"""
    last_b = [0]

    def inner(b=1, bsize=1, tsize=None):
        """
        b: int, optionala
        Number of blocks just transferred [default: 1].
        bsize: int, optional
        Size of each block (in tqdm units) [default: 1].
        tsize: int, optional
        Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return inner

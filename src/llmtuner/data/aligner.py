from functools import partial
from typing import TYPE_CHECKING, Any, Dict, List, Union

from .utils import Role


if TYPE_CHECKING:
    from datasets import Dataset, IterableDataset

    from ..hparams import DataArguments
    from .parser import DatasetAttr

example = "Example sentence 1: Mutations in SHP-2 philosophy that cause hyperactivity of its catalytic activity have been identified in human leukemias, specifically juvenile myelomonocytic leukemias." \
          "\nAnswer: From a biological perspective, overactivation of its catalytic activity is clearly a description of functional acquisition. Therefore, this sentence carries clear semantic information that the gene 'SHP-2' plays a 'GOF' function related to 'juvenile myelocytic leukemia' after mutation. Therefore, the triplet extracted from this sentence is (SHP-2, GOF, juvenile myomonosomatic leukemia). " \
          "\n\nExample sentence 2: Lynch syndrome (LS) caused by mutations in DNA mismatch repair genes MLH1. " \
          "\nAnswer: This sentence describes the association between the disease 'Lynch syndrome' and the gene 'MLH1', but the phrase 'caused by' means no loss or gain, so the triplet in this sentence should be (MLH1, REG, Lynch syndrome)." \
          "\n\nExample sentence 3: Here, we describe a fourth case of a human with a de novo KCNJ6 (GIRK2) mutation, who presented with clinical findings of severe hyperkinetic movement disorder and developmental delay Heterologous expression of the mutant GIRK2 channel one produced an additional basal award current that laminated G process activation, loss K+selectivity, and increased Ca2+permeability. " \
          "\nAnswer: The description of 'loss K+selectivity and gain Ca2+permeability' displays both LOF and GOF, so functional changes cannot be labeled as LOF or GOF, but as COM. Therefore, the triplet in this sentence should be (GIRK2, COM, hyperkinetic movement disorder)."

def convert_alpaca(examples: Dict[str, List[Any]], dataset_attr: "DatasetAttr") -> Dict[str, List[Any]]:
    outputs = {"prompt": [], "response": [], "system": [], "tools": []}
    # print('start converting...', len(examples[dataset_attr.prompt]))
    for i in range(len(examples[dataset_attr.prompt])):
        prompt = []

        instruction = examples[dataset_attr.prompt][i]
        instruction = "### Question ###\n" + instruction.replace('following', 'given')

        if dataset_attr.extra and examples[dataset_attr.extra][i]:
            instruction = "### Entities ###\n" + examples[dataset_attr.extra][i] + "\n\n\n" + instruction

        if dataset_attr.query and examples[dataset_attr.query][i]:
            instruction = '### Abstract ###\n' + examples[dataset_attr.query][i] + '\n\n\n' + instruction
            # instruction = instruction + '\n\n\n' + examples[dataset_attr.query][i]

        # if dataset_attr.example and examples[dataset_attr.example][i]:
        #     instruction = "###examples###\n" + examples[dataset_attr.example][i] + '\n\n\n' + instruction
        # if '(gene, FUNCTION CHANGE, disease)' in instruction:
        #     instruction = "###examples###\n" + example + '\n\n\n' + instruction

        prompt.append({"role": Role.USER, "content": instruction})

        if dataset_attr.response and isinstance(examples[dataset_attr.response][i], list):
            response = [{"role": Role.ASSISTANT, "content": content} for content in examples[dataset_attr.response][i]]
        elif dataset_attr.response and isinstance(examples[dataset_attr.response][i], str):
            response = [{"role": Role.ASSISTANT, "content": examples[dataset_attr.response][i]}]
        else:
            response = []

        outputs["prompt"].append(prompt)
        outputs["response"].append(response)
        outputs["system"].append(examples[dataset_attr.system][i] if dataset_attr.system else "")
        outputs["tools"].append("")

    return outputs


def align_dataset(
    dataset: Union["Dataset", "IterableDataset"], dataset_attr: "DatasetAttr", data_args: "DataArguments"
) -> Union["Dataset", "IterableDataset"]:
    r"""
    Aligned dataset:
        prompt: [{"role": "user", "content": "..."}]
        response: [{"role": "assistant", "content": "..."}]
        system: "..."
        tools: "..."
    """
    # if dataset_attr.formatting == "alpaca":
    convert_func = partial(convert_alpaca, dataset_attr=dataset_attr)
    # else:
    #     convert_func = partial(convert_sharegpt, dataset_attr=dataset_attr)

    column_names = list(next(iter(dataset)).keys())
    print('column_names: ', column_names)
    kwargs = {}
    if not data_args.streaming:
        kwargs = dict(
            num_proc=data_args.preprocessing_num_workers,
            load_from_cache_file=False,
            desc="Converting format of dataset",
        )

    return dataset.map(convert_func, batched=True, remove_columns=column_names, **kwargs)

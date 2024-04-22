import os
import json
import pandas as pd
import xml.etree.ElementTree as ET

# 对task1中与摘要拼写不符合的实体进行人工修正
correction_dic = {
    '27585885': {'gene': 'Gli2', 'disease': 'holoprosencephaly'},
    '30128655': {'gene': 'ALS2',
                 'disease': 'infantile-onset ascending hereditary spastic paralysis, juvenile primary lateral sclerosis, juvenile amyotrophic lateral sclerosis'},
    '16378925': {'gene': 'MEFV', 'disease': 'Familial Mediterranean fever'},
    '15678000': {'gene': 'LMNA', 'disease': 'Limb girdle muscular dystrophy type 1b'},
    '23072184': {'gene': 'ARX', 'disease': 'mental retardation (MR)'},
    '21868336': {'gene': 'GEN', 'disease': 'distal myopathy with rimmed vacuoles'},
    '29957067': {'gene': 'PRPF31', 'disease': 'Autosomal Dominant Retinitis Pigmentosa'},
    '29088233': {'gene': 'MSH2, MSH6', 'disease': 'Lynch syndrome'},
    '25192508': {'gene': 'TOR1A', 'disease': 'DYT1'},
    '25192508': {'gene': 'GCH1', 'disease': 'action-type dystonia'},
    '27734835': {'gene': 'FLCN', 'disease': 'Birt-Hogg-Dubé'},
    '15773749': {'gene': 'LMNA', 'disease': 'Emery-Dreifuss muscular dystrophy'},
    '24781643': {'gene': 'MVK', 'disease': 'porokeratosis of Mibelli'},
    '30702381': {'gene': 'FXIII-A', 'disease': 'Uniparental disomy'},
    '18388506': {'gene': 'FXI', 'disease': 'factor XI deficiency'},
    '26545172': {'gene': 'PIGA', 'disease': 'Simpson-Golabi-Behmel syndrome type 2'},
}

# task1 prompt
GOF = "'GOF' refers to the gain of function or the emergence of new functions \
when a gene undergoes mutation. This may include increasing or altering protein expression \
levels, enhancing activity, or causing it to be expressed at the wrong time or location. \
Gain of function mutations can lead to some abnormal phenomena, \
such as increased cell proliferation, increased metabolic rate, or triggering abnormal signal transduction."

LOF = "'LOF' refers to the partial or complete loss of function when a gene or protein undergoes mutation. \
This may include missing or altering the protein's structural domain, causing the protein to fail to \
fold properly or interact with other molecules. \
Loss of function mutations often lead to functional defects, \
which may cause genetic diseases or abnormal physiological manifestations."

COM = "'COM' refers to the more complex functional changes between genes and diseases, which may include both GOF and LOF."

REG = "'REG' refers to general regulation, without specifying whether it is a GOF or a LOF."

task1_prompt = f"Please extract (gene, FUNCTION CHANGE, disease) triplets from the following literature abstract, \
and output all the triplets in tuple format. And the possible types of FUNCTION CHANGE include: \
\n(1) {GOF}\n(2) {LOF}\n(3) {COM}\n(4) {REG}\n\
If there are no (gene, FUNCTION CHANGE, disease) triplets in the abstract, please answer \
'There are no (gene, FUNCTION CHANGE, disease) triplets.'."

# task2 prompt
task2_prompt = "Please extract (chemical, disease) relations from the following literature abstract, \
and output all the relations in tuple format. If there are no (chemical, disease) relations in the abstract, \
please answer 'There are no (chemical, disease) relations.'"

task2_prompt_chemical = "Please extract all chemical entities from the following literature abstract."
task2_prompt_disease = "Please extract all disease entities from the following literature abstract."

# task3 prompt
task3_prompt = "Please extract (drug, interaction, drug) triplets from the following literature abstract, \
and output all the triplets in tuple format. If there are no (drug, interaction, drug) triplets in the abstract, \
please answer 'There are no (drug, interaction, drug) triplets.'\nNote that the possible types of interaction \
include: \'advise', 'effect', 'int' and 'mechanism'."

name_dic = {
    'Disease': 'Disease',
    'Gene': 'Gene',
    'Protein': 'Protein',
    'Enzyme': 'Enzyme',
    'Var': 'Variation',
    'MPA': 'Molecular Physiological Activity',
    'Interaction': 'Interaction',
    'Pathway': 'Pathway',
    'CPA': 'Cell Physiological Activity',
    'Reg': 'Regulation',
    'PosReg': 'Positive Regulation',
    'NegReg': 'Negative Regulation'
}

prompt_dic = {
    'Disease': "Please extract all disease entities from the following literature abstract.",
    'Gene': "Please extract all gene entities from the following literature abstract.",
    'Protein': "Please extract all protein entities from the following literature abstract.",
    'Enzyme': "Please extract all enzyme entities from the following literature abstract.",
}


def process_task1(task1_data, triad_df, data_format=1):
    processed_data = []
    for idx, data in enumerate(task1_data):
        input_text = data['text']
        sourceid = data['sourceid']
        denotations = data['denotations']
        text = data['text']

        # 查找匹配的三元组
        matching_rows = triad_df[triad_df['PMID'] == int(sourceid)]

        output = []
        json_output = []
        for _, row in matching_rows.iterrows():
            if str(row['GENE']) == 'nan' or str(row['DISEASE']) == 'nan':
                continue

            if sourceid in correction_dic.keys():
                row['GENE'] = correction_dic[sourceid]['gene']
                row['DISEASE'] = correction_dic[sourceid]['disease']

            output.append('({}, {}, {})'.format(row['GENE'].strip(), row['FUNCTION'].strip(), row['DISEASE'].strip()))

            json_output.append({'GENE': row['GENE'].strip(),
                                'FUNCTION': row['FUNCTION'].strip(),
                                'DISEASE': row['DISEASE'].strip()})

        output = list(set(output))
        output = ', '.join(output)

        # 实体
        entity_dic = {k: [] for k in name_dic.keys()}
        for item in denotations:
            entity = text[item['span']['begin']: item['span']['end']]

            if item['obj'] not in entity_dic:
                entity_dic[item['obj']] = []

            entity_dic[item['obj']].append(entity)

        gene_output = ', '.join(list(set(entity_dic['Gene'])))
        disease_output = ', '.join(list(set(entity_dic['Disease'])))

        if gene_output == "":
            gene_output = f'There are no Gene entities.'

        if disease_output == "":
            disease_output = f'There are no Disease entities.'

        if output == '':
            output = 'There are no (gene, FUNCTION CHANGE, disease) triplets.'

        entitiy_item = []

        if data_format == 0:
            item = {
                ## "instruction"为自己定义的prompt
                "instruction": task1_prompt,
                "input": input_text,
                "response": output,
            }
        elif data_format == 1 or data_format == 2:
            item = {
                ## "instruction"为自己定义的prompt
                "instruction": task1_prompt,
                "input": input_text,
                "response": output,
            }

            entitiy_item = [{
                    ## "instruction"为自己定义的prompt
                    "instruction": prompt_dic['Gene'],
                    "input": input_text,
                    "response": gene_output,
                },
                {
                    ## "instruction"为自己定义的prompt
                    "instruction": prompt_dic['Disease'],
                    "input": input_text,
                    "response": disease_output,
                }]
        elif data_format == 3:
            item = {
                ## "instruction"为自己定义的prompt
                "instruction": task1_prompt,
                "input": input_text,
                "response": f"Let's think step by step:\n(1) Gene entities: {gene_output}\n(2) Disease entites: {disease_output}\n(3) (gene, FUNCTION CHANGE, disease) triplets: {output}",
            }
        elif data_format == 4:
            item = {
                ## "instruction"为自己定义的prompt
                "instruction": task1_prompt,
                "input": input_text,
                "response": output,
                "entity": f'Gene entities: {gene_output}\nDisease entities: {disease_output}'
            }

            entitiy_item = [{
                    ## "instruction"为自己定义的prompt
                    "instruction": prompt_dic['Gene'],
                    "input": input_text,
                    "response": gene_output,
                    "entity": ''
                },
                {
                    ## "instruction"为自己定义的prompt
                    "instruction": prompt_dic['Disease'],
                    "input": input_text,
                    "response": disease_output,
                    "entity": ''
                }]
        else:
            raise ValueError

        processed_data.append(item)
        processed_data.extend(entitiy_item)

    return processed_data


def process_task1_entity(task1_data):
    processed_data = []
    for idx, data in enumerate(task1_data):
        input_text = data['text']
        denotations = data['denotations']
        text = data['text']

        entity_dic = {k: [] for k in name_dic.keys()}
        for item in denotations:
            entity = text[item['span']['begin']: item['span']['end']]

            if item['obj'] not in entity_dic:
                entity_dic[item['obj']] = []

            entity_dic[item['obj']].append(entity)

        output = ""
        for k, v in entity_dic.items():
            if k not in ['Gene', 'Disease']:  # + ['Protein', 'Enzyme']:
                continue

            entity_output = ', '.join(list(set(v)))
            if entity_output == "":
                entity_output = f'There are no {name_dic[k]} entities.'

            entity_dic[k] = entity_output

            output += f'{name_dic[k]} Entities: {entity_output}\n'

            item = {
                "instruction": prompt_dic[k],
                "input": input_text,
                "response": entity_output,
            }

            processed_data.append(item)

    return processed_data


def list2str(relations):
    return ', '.join(f"({relation[0]}, {relation[1]})" for relation in relations)


def list2str_entity(entity_list):
    return ', '.join(entity for entity in entity_list)


def process_task2(task2_data, data_format=1):
    task2_data_new = []
    all_relations = []
    for key, value in task2_data.items():
        abstract = value['abstract']

        # 二元组
        relations = []
        for rel in value['relations']:
            chemical_id = rel['chemical']
            disease_id = rel['disease']
            # Find the corresponding names
            chemical_name = [name for name, id in value['chemical2id'].items() if id == chemical_id]
            disease_name = [name for name, id in value['disease2id'].items() if id == disease_id]

            if chemical_name and disease_name:
                relations.append((chemical_name[0], disease_name[0]))

        all_relations += [f"({rel[0]}, {rel[1]})".lower() for rel in relations]

        if len(relations) == 0:
            print('There are no (compound, disease) relations.')
        output = list2str(relations)

        # 实体
        chemical_name = [name for name, id in value['chemical2id'].items()]
        disease_name = [name for name, id in value['disease2id'].items()]

        chemical_name = list(set(chemical_name))
        disease_name = list(set(disease_name))

        chemical_output = ', '.join(chemical_name)
        disease_output = ', '.join(disease_name)

        if chemical_output == "":
            chemical_output = 'There are no chemical entities.'

        if disease_output == "":
            disease_output = 'There are no disease entities.'

        entity_item = []
        if data_format == 0:
            item = {
                "instruction": task2_prompt,
                "input": abstract,
                "response": output
            }
        elif data_format == 1 or data_format == 2:
            item = {
                "instruction": task2_prompt,
                "input": abstract,
                "response": output
            }
            entity_item = [
                {
                    "instruction": task2_prompt_chemical,
                    "input": abstract,
                    "response": chemical_output
                },
                {
                    "instruction": task2_prompt_disease,
                    "input": abstract,
                    "response": disease_output
                }

            ]
        elif data_format == 3:
            item = {
                "instruction": task2_prompt,
                "input": abstract,
                "response": f"Let's think step by step:\n(1) Chemical entities: {chemical_output}\n(2) Disease entites: {disease_output}\n(3) (chemical, disease) relations: {output}",

            }
        elif data_format == 4:
            item = {
                "instruction": task2_prompt,
                "input": abstract,
                "response": output,
                "entity": f'Chemical entities: {chemical_output}\nDisease entities: {disease_output}'
            }

            entity_item = [
                {
                    ## "instruction"为自己定义的prompt
                    "instruction": task2_prompt_chemical,
                    "input": abstract,
                    "response": chemical_output,
                    "entity": ''
                },
                {
                    ## "instruction"为自己定义的prompt
                    "instruction": task2_prompt_disease,
                    "input": abstract,
                    "response": disease_output,
                    "entity": ''
                }
            ]
        else:
            raise ValueError

        task2_data_new.append(item)
        task2_data_new.extend(entity_item)

    return task2_data_new


def process_task2_entity(task2_data):
    task2_data_new_entity = []
    for key, value in task2_data.items():
        abstract = value['abstract']

        chemical_name = [name for name, id in value['chemical2id'].items()]
        disease_name = [name for name, id in value['disease2id'].items()]

        chemical_name = list(set(chemical_name))
        disease_name = list(set(disease_name))

        chemical_name = ', '.join(chemical_name)
        disease_name = ', '.join(disease_name)

        if chemical_name == "":
            chemical_name = 'There are no chemical entities.'

        if disease_name == "":
            disease_name = 'There are no disease entities.'

        transformed_entry = {
            "instruction": task2_prompt_chemical,
            "input": abstract,
            "response": chemical_name
        }
        task2_data_new_entity.append(transformed_entry)

        transformed_entry = {
            "instruction": task2_prompt_disease,
            "input": abstract,
            "response": disease_name
        }
        task2_data_new_entity.append(transformed_entry)

    return task2_data_new_entity


def process_task3(task3_data):
    cnt = 0
    task3_data_new = []
    for key, entry in task3_data.items():
        input_text = entry['abstract']  # Extract 'abstract' for 'input'
        triples_text = ', '.join(
            [f"({triple['drug']}, {triple['interaction']}, {triple['target']})" for triple in entry['triples']])

        if triples_text == '':
            triples_text = 'There are no (drug, interaction, drug) triplets.'
            cnt += 1

        new_entry = {
            "instruction": task3_prompt,
            "input": input_text,
            "response": triples_text
        }
        task3_data_new.append(new_entry)

    return task3_data_new


def parse_xml(data_dir):
    files = os.listdir(data_dir)

    ddi_data = []
    for file in files:
        if not file.endswith('.xml'):
            continue
        tree = ET.parse(os.path.join(data_dir, file))  # 解析XML文件
        root = tree.getroot()  # 获取根元素
        item = {}

        text = ''
        triples = []
        pmid = ''
        for child in root:  # 遍历子元素
            text += child.attrib['text']
            pmid = '.'.join(child.attrib['id'].split('.')[:-1])
            entity_dic = {}
            for sub_child in child:
                if sub_child.tag == 'entity':  # and sub_child.attrib['type'] == 'drug':
                    entity_dic[sub_child.attrib['id']] = sub_child.attrib['text']
                if sub_child.tag == 'pair' and sub_child.attrib['ddi'] == 'true':
                    try:
                        triples.append(
                            {'drug': entity_dic[sub_child.attrib['e1']], 'target': entity_dic[sub_child.attrib['e2']],
                             'interaction': sub_child.attrib['type']})
                    except:
                        print(pmid)
                        continue
        item['abstract'] = text
        item['triples'] = triples
        item['pmid'] = pmid

        ddi_data.append(item)

    return ddi_data


def parse_txt(data_dir):
    files = os.listdir(data_dir)
    file_names = list(set([f.split('.')[0] for f in files if f.endswith('.txt') or f.endswith('.ann')]))
    ddi_data = []

    for name in file_names:
        with open(os.path.join(data_dir, f'{name}.txt'), 'r') as fr:
            lines = fr.readlines()
        abstract = ''.join(lines)

        with open(os.path.join(data_dir, f'{name}.ann'), 'r') as fr:
            lines = fr.readlines()
        drug_dict = {}
        triples = []
        for l in lines:
            tmp_list = l.strip().split('\t')

            if len(tmp_list) == 3:
                id_, type_, drug = tmp_list
                drug_dict[id_] = drug

            elif len(tmp_list) == 2:
                interaction, arg1, arg2 = tmp_list[-1].split(' ')
                try:
                    arg1 = drug_dict[arg1.split(':')[1]]
                    arg2 = drug_dict[arg2.split(':')[1]]

                    if arg1.lower() not in abstract.lower() or arg2.lower() not in abstract.lower():
                        continue

                    triples.append({'drug': arg1, 'target': arg2, 'interaction': interaction.lower()})
                except:
                    print(arg1, arg2)
                    print(name)
        item = {}
        item['abstract'] = abstract
        item['triples'] = triples
        item['pmid'] = name

        ddi_data.append(item)

    return ddi_data


def get_external_task2_data(data_dir):
    files1 = os.listdir(data_dir)
    files1 = [f for f in files1 if f.endswith('.txt')]

    lines = []
    for file in files1:
        with open(os.path.join(data_dir, file), 'r') as fr:
            lines += fr.readlines()

    i = 0
    external_task2_data = {}
    while i < len(lines):
        pid, title = lines[i].strip().split('|t|')
        i += 1
        pid, text = lines[i].strip().split('|a|')
        i += 1
        checmical2id, id2checmical = {}, {}
        disease2id, id2disease = {}, {}
        relations = []
        while i < len(lines) and lines[i] != '\n':
            arr = lines[i].strip().split('\t')

            if len(arr) == 6:
                name, type_, id_ = arr[3:]

                if type_ == 'Disease':
                    disease2id[name] = id_
                    id2disease[id_] = name
                elif type_ == 'Chemical':
                    checmical2id[name] = id_
                    id2checmical[id_] = name
            elif len(arr) == 7:
                type_, id_, name = arr[4:]
                id_list = id_.split('|')
                name_list = name.split('|')

                for j in range(len(id_list)):
                    if type_ == 'Disease':
                        disease2id[name_list[j]] = id_list[j]
                        id2disease[id_list[j]] = name_list[j]
                    elif type_ == 'Chemical':
                        checmical2id[name_list[j]] = id_list[j]
                        id2checmical[id_list[j]] = name_list[j]

            elif len(arr) == 4:
                id1, id2 = arr[2:]
                relations.append({'chemical': id1, 'disease': id2})
            else:
                raise ValueError

            i += 1

        if lines[i] == '\n':
            i += 1

        item = {
            'title': title,
            'abstract': text,
            'chemical2id': checmical2id,
            'disease2id': disease2id,
            'relations': relations
        }

        external_task2_data[pid] = item

    return external_task2_data


def get_external_task3_data(ddi_data_dir2, ddi_data_dir3):
    train_ddi_data = []

    ### ddicorpus2013
    train_drugbank_dir2 = os.path.join(ddi_data_dir2, 'Train', 'DrugBank')
    train_ddi_data += parse_xml(train_drugbank_dir2)

    train_medline_dir2 = os.path.join(ddi_data_dir2, 'Train', 'MedLine')
    train_ddi_data += parse_xml(train_medline_dir2)

    abstracts = [d['abstract'] for d in train_ddi_data]

    print(len(train_ddi_data))

    ### ddicorpus2013(brat)
    train_drugbank_dir3 = os.path.join(ddi_data_dir3, 'Train', 'DrugBank')
    ddi_data = parse_txt(train_drugbank_dir3)
    ddi_data = [d for d in ddi_data if d['abstract'] not in abstracts]
    train_ddi_data += ddi_data

    train_medline_dir3 = os.path.join(ddi_data_dir3, 'Train', 'MedLine')
    ddi_data = parse_txt(train_medline_dir3)
    ddi_data = [d for d in ddi_data if d['abstract'] not in abstracts]
    train_ddi_data += ddi_data

    print(len(train_ddi_data))

    test_ddi_data = []

    ### ddicorpus2013
    test_drugbank_dir2 = os.path.join(ddi_data_dir2, 'Test', 'Test for DDI Extraction task', 'DrugBank')
    test_ddi_data += parse_xml(test_drugbank_dir2)
    print(len(test_ddi_data))
    abstracts = [d['abstract'] for d in test_ddi_data]

    ### ddicorpus2013(brat)
    test_drugbank_dir3 = os.path.join(ddi_data_dir3, 'Test', 'DrugBank')
    ddi_data = parse_txt(test_drugbank_dir3)
    ddi_data = [d for d in ddi_data if d['abstract'] not in abstracts]
    test_ddi_data += ddi_data
    print(len(test_ddi_data))

    test_medline_dir3 = os.path.join(ddi_data_dir3, 'Test', 'MedLine')
    ddi_data = parse_txt(test_medline_dir3)
    ddi_data = [d for d in ddi_data if d['abstract'] not in abstracts]
    test_ddi_data += ddi_data

    len(test_ddi_data)

    external_task3_data = train_ddi_data + test_ddi_data

    return external_task3_data


def process_data(data_dir, test_path, external_task2_data_dir, ddi_data_dir1, ddi_data_dir2, data_format=1):
    '''官方训练集 预处理'''

    # task1
    task1_files = os.listdir(os.path.join(data_dir, 'task1'))
    all_lines = []
    for file in task1_files:
        if not file.endswith('json'):
            continue
        with open(os.path.join(data_dir, 'task1', file), 'r') as fr:
            lines = fr.readlines()

        all_lines += lines

    task1_data = [json.loads(l) for l in all_lines]
    task1_train_triad = pd.read_excel(os.path.join(data_dir, 'task1', 'train_triad.xlsx'))

    task1_data_new = process_task1(task1_data, task1_train_triad, data_format)
    # task1_data_new_entity = process_task1_entity(task1_data)

    print('Task1 data done.')

    # task2
    fr = open(os.path.join(data_dir, 'task2', 'train.json'), 'r')
    content = fr.read()
    task2_data = json.loads(content)

    task2_data_new = process_task2(task2_data, data_format)
    # task2_data_new_entity = process_task2_entity(task2_data)

    # task3
    fr = open(os.path.join(data_dir, 'task3', 'train.json'), 'r')
    content = fr.read()
    task3_data = json.loads(content)

    task3_data_new = process_task3(task3_data)

    # test data A
    with open(test_path, 'r') as fr:
        lines = fr.readlines()

    test_text_dic = {1: [], 2: [], 3: []}
    for idx, l in enumerate(lines):
        data = json.loads(l)
        task_id = data['task']
        if task_id == 1 or task_id == 3:
            text = data['text']
        else:
            text = data['abstract']
        test_text_dic[task_id].append(text)

    '''外部训练集 预处理'''
    # task2
    external_task2_data = get_external_task2_data(external_task2_data_dir)
    external_task2_data_new = process_task2(external_task2_data, data_format)
    # external_task2_data_new_entity = process_task2_entity(external_task2_data)

    # 去除A榜中测试集
    task2_texts = [d['input'] for d in task2_data_new] + test_text_dic[2]
    external_task2_data_new = [d for d in external_task2_data_new if d['input'] not in task2_texts]
    print(len(external_task2_data_new))

    # external_task2_data_new_entity = [d for d in external_task2_data_new_entity if d['input'] not in task2_texts]
    # print(len(external_task2_data_new_entity))

    # task3
    external_task3_data = get_external_task3_data(ddi_data_dir1, ddi_data_dir2)
    external_task3_data_new = []
    for entry in external_task3_data:
        input_text = entry['abstract']  # Extract 'abstract' for 'input'
        triples_text = ', '.join(
            [f"({triple['drug']}, {triple['interaction']}, {triple['target']})" for triple in entry['triples']])

        if triples_text == '':
            print('There are no (drug, interaction, drug) triplets.')
            triples_text = 'There are no (drug, interaction, drug) triplets.'

        new_entry = {
            "instruction": task3_prompt,
            "input": input_text,
            "response": triples_text
        }
        external_task3_data_new.append(new_entry)

    # 去除A榜中的task3数据
    task3_texts = [d['input'] for d in task3_data_new] + test_text_dic[3]
    external_task3_data_new = [d for d in external_task3_data_new if d['input'] not in task3_texts]
    print(len(external_task3_data_new))

    '''数据保存'''
    # task1
    with open(f'./data/train_data_task1_{data_format}.json', 'w') as fw:
        for d in task1_data_new:
            fw.write(json.dumps(d, ensure_ascii=False) + '\n')

    # task2
    with open(f'./data/train_data_task2_{data_format}.json', 'w') as fw:
        for d in task2_data_new + external_task2_data_new:
            fw.write(json.dumps(d, ensure_ascii=False) + '\n')

    # task3
    with open(f'./data/train_data_task3_{data_format}.json', 'w') as fw:
        for d in task3_data_new + external_task3_data_new:
            fw.write(json.dumps(d, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    import argparse
    args = argparse.ArgumentParser()
    args.add_argument('--data_format', default=0, type=int)

    args = args.parse_args()

    data_dir = './data/AGAC-GDA_v8'
    test_path = './data/data/dataA/submission.jsonl'
    external_task2_data_dir = './data/external_data/BioCreative-V-CDR-Corpus-master/CDR_Data/CDR_Data/CDR.Corpus.v010516'
    ddi_data_dir1 = './data/external_data/DDICorpus/DDICorpus-2013/DDICorpus'
    ddi_data_dir2 = './data/external_data/DDICorpus/DDICorpus-2013(BRAT)/DDICorpusBrat'
    process_data(data_dir, test_path, external_task2_data_dir, ddi_data_dir1, ddi_data_dir2, data_format=args.data_format)

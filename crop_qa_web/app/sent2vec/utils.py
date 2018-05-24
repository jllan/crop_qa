import os
import pickle
import subprocess
import jieba
import json
from subprocess import call
import re


DATA_DIR = os.path.join('/media/jlan/E/Projects/crop_qa_web/app/sent2vec/data')
FASTTEXT_EXEC_PATH = os.path.join(DATA_DIR, 'fasttext')
MODEL_FILE = os.path.join(DATA_DIR, 'rice_model.bin')    # Sent2Vec训练生成的模型
STOP_WORDS = os.path.join(DATA_DIR, 'stop_words.txt')

TRAIN_FILE = os.path.join(DATA_DIR, 'rice_corp_train.txt') # Sent2Vec训练句向量的语料
CORPORA = os.path.join(DATA_DIR, 'rice_q_cut_distinct.txt') # 计算与其中最相似的问题
CORPORA_DICT = os.path.join(DATA_DIR, 'rice_q_id.json') # {问题：id}，从CORPORA中找到最相似问题后，再从该文件中找出最相似问题的id
TEST_FILE = os.path.join(DATA_DIR, 'user_question.txt') # 用户输入的问题先写入该问句


def train(fasttext_exec_path, input_file, output_model):
    # train_command = '{} sent2vec -input {} -output {} -minCount 8 -dim 700 -epoch 9 -lr 0.2 -wordNgrams 2 -loss ns ' \
    #                 '-neg 10 -thread 20 -t 0.000005 -dropoutK 4 -minCountLabel 20 -bucket 4000000'\
    #     .format(fasttext_exec_path, input_file, output_model)

    train_command = '{} sent2vec -input {} -output {}'.format(fasttext_exec_path, input_file, output_model)
    print(train_command)
    call(train_command, shell=True)


def cut_words(sentence):
    sentence = re.sub('<.*?>', '', sentence).strip()
    sentence = re.sub('[\W+\s+\d+a-zA-Z]', '', sentence)
    with open(os.path.join(DATA_DIR, 'stop_words.txt'), 'r') as f:
        stop_words = [word.strip() for word in f.readlines()if word.strip()]
    word_list = jieba.cut(sentence)
    # word_list = [word.strip() for word in word_list if word.strip() and word.strip() not in stop_words]
    word_list = [word.strip() for word in word_list if word.strip()] # 不去停用词
    return word_list


def get_nnSent(fasttext_exec_path, model_file, corpora, test_file, k):
    """执行"fasttext nnSent model.bin corpora.txt [k]，找到相似句子"""
    test_command = '{} nnSent {} {} {} {}' \
        .format(FASTTEXT_EXEC_PATH, model_file, corpora, test_file, k)
    result = subprocess.check_output(test_command, shell=True)
    result = result.decode('utf8')
    # 当检查准确率时需要先将结果写入文件
    with open(os.path.join(DATA_DIR, 'computing_accuracy/nnSent.txt'), 'w') as f:
        f.write(result)
    result = result.split('\n')[2:]
    result = [i.split(',')[0].strip() for i in result if i.strip()]
    return result


def search(text):
    word_list = cut_words(text)
    with open(TEST_FILE, 'w') as f:
        f.write(' '.join(word_list))
    result = get_nnSent(FASTTEXT_EXEC_PATH, MODEL_FILE, CORPORA, TEST_FILE, k=3)
    f = open(CORPORA_DICT, encoding='utf-8')
    q_dict = json.load(f)
    result_id = [q_dict.get(i) for i in result]
    return result, result_id


def compute_precision(result, k):
    std_sim_dict = json.load(open(os.path.join(DATA_DIR, 'computing_accuracy/part_sim_qs_cut.json'), encoding='utf-8'))
    num_std_q = len(std_sim_dict)  # 标准问题数量
    num_sim_q = sum([len(i) for i in std_sim_dict.values()])  # 相似问题数量，一个标准问题可能对应多个相似问题
    num_correct = 0  # 预测正确的数量

    # 从get_nnSent函数生成的结果中读取，每k+1行为一个单元，第一行是相似问题，后k行是找出的最接近的k个标准问题
    with open(result, 'r') as f:
        lines = [line.strip() for line in f.readlines()[1:] if line.strip()]
    results_each = [lines[i:i + k + 1] for i in range(0, len(lines), k + 1)]
    num_std_q2 = len(results_each)

    for result_each in results_each:
        std_q = result_each[0]  # 问题
        sim_qs = [v.split(',')[0].strip() for v in result_each[2:]]  # 计算出的与之相似的问题
        find = False
        for j in range(k - 1):
            sims = std_sim_dict.get(std_q)
            if sims:  # 有的标准问题没有与之对应的相似问题
                if sim_qs[j] in sims:  # 从相似问题预测出每一个标准问题中反向查找相似问题，如果找到该相似问题，则预测成功
                    num_correct += 1
                    find = True
                    break
        if not find:
            print('std: ', std_q)
            print('predict sims: ', sim_qs)
            print('correct sims: ', sims)
            print('\n')
    print('num_correct:', num_correct)
    print('num_std_q:', num_std_q)
    print('num_sim_q:', num_sim_q)
    print('num_std_q2:', num_std_q2)
    print('accuracy: ', num_correct / num_std_q2)


if __name__ == '__main__':
    # train(FASTTEXT_EXEC_PATH, TRAIN_FILE, MODEL_FILE)

    k = 2

    result = get_nnSent(FASTTEXT_EXEC_PATH, MODEL_FILE, os.path.join(DATA_DIR, 'computing_accuracy/part_qs_corp.txt'), os.path.join(DATA_DIR, 'computing_accuracy/test.txt'), k)

    compute_precision(os.path.join(DATA_DIR, 'computing_accuracy/nnSent.txt'), k)

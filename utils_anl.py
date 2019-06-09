import psutil
from threading import Thread
from subprocess import PIPE
from queue import Queue, Empty
import time
import pickle
import tensorflow as tf
from keras.models import load_model
import numpy as np

tf.logging.set_verbosity(tf.logging.ERROR)


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        # print(line)
        queue.put(line)
    out.close()


def update_data(input_line, per_cpu):
    #  1.000418172 CPU1                40.462      r205
    #  1.000472956,CPU5,25933,,r105,1000277655,100,00,,
    input_line = input_line.decode('utf-8').strip()
    splitted = input_line.split(',')
    if per_cpu:
        cpu = int(splitted[1][-1])
        value = int(splitted[2])
        hpc = splitted[4]
        return cpu, value, hpc
    else:
        value = int(splitted[1])
        hpc = splitted[3]
        return value, hpc


# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def crypto_anl():
    scaler_file = './ai/scaler_pck.save'
    feat_file = './ai/sel_nn_features.txt'
    model_file = './ai/selected_nn_best.h5'
    secs_to_monitor = '1'
    nr_of_cpu = psutil.cpu_count()
    q = Queue()
    data = {}

    print('Start Analysis...')
    print('Getting features...')

    with open(feat_file) as inf:
        temp_line = inf.readline().strip()

    feats = [x.strip() for x in temp_line.split()]
    feats_copy = list.copy(feats)

    for i in range(nr_of_cpu):
        temp_feat_dict = {}
        for feat in feats:
            temp_feat_dict[feat] = []
        data[i] = temp_feat_dict

    if len(feats) % 4 == 1:
        total_secs_of_anl = len(feats) / 4
    else:
        total_secs_of_anl = len(feats) / 4 + 1

    counter = 0
    while feats:
        this_batch = feats[:4]
        del feats[:4]
        events_str = ''
        for one_feat in this_batch:
            events_str = events_str + '-e ' + one_feat + ' '
        events_str = 'perf stat ' + events_str + '-I 1000 -a -A -x , sleep ' + secs_to_monitor + ' ; '

        perf_handler = psutil.Popen(events_str, stderr=PIPE, shell=True)
        t = Thread(target=enqueue_output, args=(perf_handler.stderr, q))
        t.daemon = True
        t.start()

        cnt = 0
        while perf_handler.is_running():
            while True:
                try:
                    if q:
                        line = q.get(timeout=.1)
                        cpu, value, hpc = update_data(line, True)
                        data[cpu][hpc].append(value)
                    else:
                        break
                except Empty:
                    break

            if cnt >= int(secs_to_monitor):
                perf_handler.kill()
                break
            cnt += 1
            time.sleep(1)

        counter += 1
        print_progress_bar(int(counter * 100 / total_secs_of_anl), 100, prefix='Progress:', suffix='Complete',
                           length=10)
    print_progress_bar(100, 100, prefix='Progress:', suffix='Complete', length=10)

    with open(scaler_file, 'rb') as inf:
        scaler_f = pickle.load(inf)

    found_thread = False
    model = load_model(model_file)
    for i in range(nr_of_cpu):
        for j in range(int(secs_to_monitor)):
            model_input = []
            for feat in feats_copy:
                model_input.append(data[i][feat][j])
            model_input = np.array(model_input).astype(float).reshape(1, -1)
            input_scaled = scaler_f.transform(model_input)
            res = model.predict_classes(input_scaled)
            if res:
                found_thread = True

    if found_thread:
        print('Possible threat found!')
        max_proc = None
        for proc in psutil.process_iter(attrs=['pid', 'exe', 'cpu_percent']):
            proc_dict = proc.info
            if max_proc:
                if proc_dict['cpu_percent'] > max_proc['cpu_percent']:
                    max_proc = proc_dict
            else:
                max_proc = proc_dict
        print(str(max_proc['pid']) + ' ' + max_proc['exe'])
    else:
        print('No threat found!')


from urllib import request
import csv


content = []
with open('/proc/cpuinfo') as inf:
    content = inf.readlines()

vendor_id = content[1].split(':')[1].strip()
cpu_family = content[2].split(':')[1].strip()
model = int(content[3].split(':')[1].strip())
model = format(model, 'X')
stepping = content[5].split(':')[1].strip()

look_for = vendor_id+'-'+cpu_family+'-'+model

map_file_raw = request.urlopen('https://download.01.org/perfmon/mapfile.csv')
map_file = (map_file_raw.read().decode('utf-8')).split('\n')

core_path = ''

for line in map_file:
    row = line.split(',')

    if look_for in row[0]:
        if row[-1] in 'core':
            core_path = row[2]
            break

core_file_raw = request.urlopen('https://download.01.org/perfmon'+core_path)
core_file = core_file_raw.read().decode('utf-8')
with open('hpc_info.txt', 'w') as otf:
    otf.write(core_file)

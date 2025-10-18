import os

path_base = 'data'
i = 'gcc-1K.memtrace'
path_data = os.path.join(path_base, i)


# strs_instruction = ['L -200 7fffe7ff088','L 0 7fffe7fefd0'] * 1000

with open(path_data,'r') as file:

    strs_instruction = file.read().splitlines()
    for str_instruction in strs_instruction[:10]:
        str_instruction = str_instruction.rstrip()
        print(str_instruction)
    # end
# end


import json
import glob
from pathlib import Path
import math 

model="doctr_gpu"

# Get images
list_of_files = glob.glob("{}/*.json".format(model))
print("\n\nFound {} files for model {}.".format(len(list_of_files), model))


data_file = '{}.csv'.format(model)
wordfile = open(data_file, "w")
wordfile.write("filename|model|word|confidence|vertices_x_0|vertices_y_0|vertices_x_1|vertices_y_1|vertices_x_2|vertices_y_2|vertices_x_3|vertices_y_3\n")

# Run each file
for filename in list_of_files:
    file_stem = Path(filename).stem
    # Open file
    print("Reading json file {}...".format(file_stem))
    with open(filename, 'r') as file:
        data = json.load(file)
    dimensions = data['dimensions']
    dim_h = math.ceil(dimensions[0] * 1.0)
    dim_v = math.ceil(dimensions[1] * 1.0)
    blocks = data['blocks']
    if len(blocks) == 0:
        # Nothing was found
        wordfile.write("{}|{}|{}|{}|{}|{}|{}||||\n".format(file_stem, model, "NA", "", "", "", "", ""))
        continue
    else:
        # Blocks were found, iterate
        for block in blocks:
            for line in block['lines']:
                for word in line['words']:
                    wordfile.write("{}|{}|{}|{}|{}|{}|{}|{}||||\n".format(file_stem, model, word['value'], word['confidence'], math.ceil(word['geometry'][0][0]*dim_h) + 5.0, math.ceil(word['geometry'][0][1]*dim_h), math.ceil(word['geometry'][1][0]*dim_v), math.ceil(word['geometry'][1][1])*dim_v))



wordfile.close()

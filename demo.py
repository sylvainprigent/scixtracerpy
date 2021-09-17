import os
import numpy as np
from skimage import io, restoration, transform

import scixtracer as sx

# First we connect to the database (here it is a local database)
req = sx.Request()

# Create an experiment
experiment = req.create_experiment(name='myexperiment',
                                   author='sprigent',
                                   date='now',
                                   destination="./")

# Import a directory of data to the experiment
req.import_dir(experiment=experiment,
               dir_uri='./tests/test_images/data',
               filter_=r'\.tif$',
               author='sprigent',
               format_='tif',
               date='now',
               copy_data=True)

# Tag the images using the information in the file names
req.tag_from_name(experiment, 'Population', ['population1', 'population2'])
req.tag_using_separator(experiment, 'ID', '_', 1)

# Request a data using tags
raw_dataset = req.get_dataset(experiment, name="data")
raw_data_list = req.get_data(raw_dataset, "Population=population1 AND ID=001")
print("query result:")
for raw_data in raw_data_list:
    print('\t'+raw_data.name)

# Now we want to run a Wiener deconvolution of each images
# First we create a dataset to store the result
processed_dataset = req.create_dataset(experiment, "wiener")

# then we create the metadata of the Wiener deconvolution
run_info = sx.Run()
run_info.set_process(name='wiener', uri='uniqueIdOfWiener')
run_info.add_input(name='image', dataset='data')  # no query so we select all
regularization = 1
run_info.add_parameter('regularization', str(regularization))
req.create_run(processed_dataset, run_info)  # save to database

# then we loop on all the images using a query
data_list = req.get_data(raw_dataset, query="")  # all data in raw dataset
for data in data_list:
    # create the wiener processed image matadata
    out_file = os.path.abspath(os.path.join("myexperiment", "wiener",
                                            "o_" + data.name))
    processed_data = sx.ProcessedData()
    processed_data.set_info(name="o_" + data.name, author="sprigent",
                            date='now', format_="tif", url=out_file)
    processed_data.add_input(id="i", data=data)
    processed_data.set_output(id="o", label="wiener deconv")
    req.create_data(processed_dataset, run_info, processed_data)

    # run the Wiener deconvolution
    img = io.imread(data.uri)
    psf = np.ones((2, 2)) / 4
    img_rescaled = transform.rescale(img, 0.5)
    out_img = restoration.wiener(img_rescaled, psf, regularization)
    io.imsave(out_file, out_img)

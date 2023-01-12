import os
from scipy.io import loadmat
import numpy as np
from typing import Union
from PIL import Image

class CompiledDataset:
    """
    ## CompiledDataset
    Used to represent the EMNIST datasets located at "data\\EMNIST". Provides an easy way to gather batches of
    samples which has a validation partition that, if specified, will be provided as a means to measure the 
    performance of the model. The length of this partition is determined by the length of the test data which
    also is accessible with this class.

    ### Args:
    dataset_filename: String argument needs to be a valid file name within the EMNIST data folder

    validation_partition: Booleon determining wheter or not to extract validation data

    https://www.nist.gov/itl/products-and-services/emnist-dataset
    """
    __data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    def __init__(self, *,
        filename: str,
        validation_partition: bool, 
        as_array: bool, 
        flatten: bool,
        normalize: bool
    ):
        filepath = os.path.join(self.__data_dir, "EMNIST", filename)

        if not os.path.exists(filepath):
            raise Exception("Dataset not found! Download the EMNIST dataset from Google Drive")

        self.__data = loadmat(filepath, simplify_cells = True)["dataset"]
        self.__as_array = as_array
        self.__flatten = flatten
        self.__normalize = normalize

        training_len = len(self.__data["train"]["labels"])
        partition_len = len(self.__data["test"]["labels"])

        self.new_training_data = lambda: self.__create_labeled_generator("train", slice(0, training_len - partition_len*validation_partition))
        self.training_data = self.__create_labeled_generator("train", slice(0, training_len - partition_len*validation_partition))
        self.test_data = self.__create_labeled_generator("test", slice(0, partition_len))
        self.validation_data = self.__create_labeled_generator("train", slice(training_len - partition_len*validation_partition, training_len))

        self.training_len = training_len - partition_len*validation_partition
        self.validation_len = partition_len*validation_partition

        if self.__flatten and self.__as_array:
            img, lbl = next(self.training_data)
            self.shape = (len(img), len(lbl))
        else:
            self.shape = (None, None)

    def represent(self, array, label):
        image = (array.reshape(28,28) + 1) * 127.5 if self.__normalize else array.reshape(28,28)
        if label is None:
            return image if self.__flatten else array
        _ascii = self.__data["mapping"][label.tolist().index(1)][1]
        return (image if self.__flatten else array,
                chr(_ascii) if self.__as_array else label)

    def show(self, array, label):
        Image.fromarray(array).show()
        print(label)

    def __label_type(self, label: str) -> Union[str, np.ndarray]:
        index = label-self.__data["mapping"][0][0]
        if not self.__as_array: return chr(self.__data["mapping"][index][1])
        out = np.zeros(len(self.__data["mapping"]))
        out[index] = 1
        return out

    def __create_labeled_generator(self, target: str, interval: slice):
        assert target in ["train", "test"], "arg. target not of type 'train', 'test' or 'validation'"
        targeted_data = self.__data[target]
        for image, label in zip(targeted_data["images"][interval], targeted_data["labels"][interval]):
            image = np.flip(np.rot90(np.reshape(image, (28, 28)), -1), -1)

            # argument clauses
            image = image.flatten() if self.__flatten else image
            # image = image / 127.5 - 1 if self.__normalize else image # -1 to 1
            # image = image / 255 if self.__normalize else image # 0 to 1
            image = (image - np.mean(image)) / np.std(image) if self.__normalize else image # mean 0, std 1

            yield (image, self.__label_type(label))

    def next_batch(self, batch_size: int):
        for _ in range(batch_size):
            sample = next(self.training_data, None)
            if sample == None:
                self.training_data = self.new_training_data()
                next(self.training_data)
                break
            yield sample
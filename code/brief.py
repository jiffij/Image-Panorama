import numpy as np
import scipy.stats as st
import math
from tqdm import tqdm

class Brief:

    def __init__(self, kernel_size=21, bits=128):
        """
        This Brief class used gaussian distribution to select point pairs.
        :param kernel_size: The rectangular box used for every keypoint, better to be odd number
        :param bits: 128 or 256 bits 
        """
        self.kernel = self.__gaussian_kernel(kernel_size)
        self.kernel_size = kernel_size
        self.bits = bits
        self.pt_pairs = []
        self.kernel_half_len = math.ceil(kernel_size/2)
        flatten_kernel = self.kernel.flatten()
        pos = np.arange(0, len(flatten_kernel))
        for i in range(bits):
            random_a = np.random.choice(pos, p=flatten_kernel)
            random_b = np.random.choice(pos, p=flatten_kernel)
            self.pt_pairs.append((random_a, random_b))

    @staticmethod
    def __gaussian_kernel(kernel_size, nsig=3):
        # Initializing value of x,y as grid of kernel size
        # in the range of kernel size

        # x, y = np.meshgrid(np.linspace(-1, 1, kernel_size),
        #                    np.linspace(-1, 1, kernel_size))
        # dst = np.sqrt(x ** 2 + y ** 2)

        # # lower normal part of gaussian
        # normal = 1 / ( math.sqrt(2*math.pi) * std)

        # # Calculating Gaussian filter
        # gauss = np.exp(-((dst - mean) ** 2 / (2.0 * std ** 2))) * normal
        # return gauss
        x = np.linspace(-nsig, nsig, kernel_size+1)
        kern1d = np.diff(st.norm.cdf(x))
        kern2d = np.outer(kern1d, kern1d)
        kern2d = kern2d/kern2d.sum()
        # print(kern2d)
        return kern2d

    def __describe(self, image, x, y):
        # print(x-self.kernel_size/2)
        rectangle = image[x-self.kernel_half_len:x+self.kernel_half_len, y-self.kernel_half_len:y+self.kernel_half_len]
        flatten_rectangle = rectangle.flatten()
        bit_str = ""
        for pair in self.pt_pairs:
            try:
                bit_str += "1" if flatten_rectangle[pair[0]] < flatten_rectangle[pair[1]] else "0"
            except IndexError:
                return 0
        return int(bit_str, base=2)

    @staticmethod
    def __hamming_dist(descriptor_1, descriptor_2):
        """
        compute the hamming distance between all pairs of key points
        :param descriptor_1: 128-bits or 256-bits binary int
        :param descriptor_2: 128-bits or 256-bits  binary int
        :return: hamming distance (int)
        """
        xor = descriptor_1 ^ descriptor_2
        return bin(xor).count("1")

    def get_threshold_pairs(self, descriptors_1, descriptors_2, location_1, location_2, threshold):
        """
        This function compute the hamming distance between all key points pairs, and return only pairs with hamming distance less than threshold
        :param descriptors_1: list of binary int
        :param descriptors_2: list of binary int
        :param location_1: np.array()
        :param location_2: np.array()
        :param threshold: less is better
        :return: list of tuples of location
        """
        diff = np.zeros(shape=(len(descriptors_1), len(descriptors_2)))
        # print(len(descriptors_1), len(descriptors_2))
        for row in tqdm(range(len(descriptors_1))):
            for col in range(len(descriptors_2)):
                diff[row][col] = self.__hamming_dist(descriptors_1[row], descriptors_2[col])
        diff = diff < threshold
        a, b = np.nonzero(diff)
        return [(location_1[i], location_2[j]) for i, j in zip(a, b)]

    def compute(self, image, keypoints):
        """
        BRIEF detector converts the given keypoints into 128 or 256 bit encoding
        :param image: a gray scale image 2 dim array (HxW)
        :param keypoints: an array of keypoint positions
        :return: descriptor, keypoint position
        """
        descriptors = list()
        locations = list()
        for keypoint in keypoints:
            descriptor = self.__describe(image, keypoint[0], keypoint[1])
            if descriptor > 0:
                descriptors.append(descriptor)
                locations.append((keypoint[0], keypoint[1]))
            else:
                continue
        return descriptors, locations




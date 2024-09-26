#################################################################
# FILE : image_editor.py
# WRITER : guy fussfeld , guy_fussfeld , 207766973
# EXERCISE : intro2cs ex5 2022-2023
# DESCRIPTION: A simple program that edit images
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES:
#################################################################

##############################################################################
#                                   Imports                                  #
##############################################################################
from ex5_helper import *
from typing import Optional
import math
import sys
import copy

##############################################################################
#                                  Functions                                 #
##############################################################################

# gets a 3 dimensional list of colorful picture and split the list into the different channels


def separate_channels(image: ColoredImage) -> List[SingleChannelImage]:
    image_lst = []
    number_of_rows = len(image)
    number_of_channels = len(image[0][0])
    for channels in range(number_of_channels):
        current_channel_lst = []
        for rows in range(number_of_rows):
            current_channel_lst.append([column[channels]
                                       for column in image[rows]])
        image_lst.append(current_channel_lst)
    return image_lst

# does the oposite of the last fucnction


def combine_channels(channels: List[SingleChannelImage]) -> ColoredImage:
    image = []
    number_of_columns = len(channels[0])
    number_of_channels = len(channels[0][0])
    for columns in range(number_of_columns):
        current_column_lst = []
        for channelsa in range(number_of_channels):
            current_column_lst.append(
                [rows[columns][channelsa] for rows in channels])
        image.append(current_column_lst)
    return image

# gets a list or rgb (3 ints) and return an imerge of the three (an int)


def color_to_gray(rgb_lst):
    a = round(rgb_lst[0]*0.299+rgb_lst[1]*0.587+rgb_lst[2]*0.114)
    if a > 255:
        a = 255
    if a < 0:
        a = 0
    return a

# gets an rgb picture picture and return a gray one


def RGB2grayscale(colored_image: ColoredImage) -> SingleChannelImage:
    single_channel = []
    number_of_rows = len(colored_image)
    number_of_columns = len(colored_image[0])
    for rows in range(number_of_rows):
        current_row = []
        for columns in range(number_of_columns):
            current_row.append(color_to_gray(colored_image[rows][columns]))
        single_channel.append(current_row)
    return single_channel

# gets an int and return a kernel with the size of size**2 the have 1/size**2 values


def blur_kernel(size: int) -> Kernel:
    kernel2 = []
    for a in range(size):
        kernel1 = []
        for b in range(size):
            kernel1.append(1/(size**2))
        kernel2.append(kernel1)
    return kernel2

# gets a one channel picture and a kernel and return a blurred version of the image


def apply_kernel(image: SingleChannelImage, kernel: Kernel) -> SingleChannelImage:
    mid_kernel = len(kernel)//2
    num_rows = len(image)
    num_columns = len(image[0])
    blurred_image = []
    sum = 0
    for row in range(num_rows):
        current_row = []
        for column in range(num_columns):
            for a in range(len(kernel)):
                for b in range(len(kernel)):
                    # checks if the index is in the list
                    if row-mid_kernel+a < 0 or row-mid_kernel+a > num_rows-1 or column-mid_kernel+b < 0 or column-mid_kernel+b > num_columns-1:
                        sum += image[row][column]*kernel[a][b]
                    else:
                        sum += image[row-mid_kernel+a][column -
                                                       mid_kernel+b]*kernel[a][b]
            sum = round(sum)
            if sum > 255:
                sum = 255
            if sum < 0:
                sum = 0
            current_row.append(sum)
            sum = 0
        blurred_image.append(current_row)
    return blurred_image

# does an interpolation on a pixel from source to destination


def bilinear_interpolation(image: SingleChannelImage, y: float, x: float) -> int:
    if y > len(image)-1:
        y = math.floor(y)
    if x > len(image[0])-1:
        x = math.floor(x)
    if y < 0:
        y = 0
    if x < 0:
        x = 0
    a_y = math.ceil(y)-1
    a_x = math.ceil(x)-1
    if a_y < 0:
        a_y = 0
    if a_x < 0:
        a_x = 0
    a = image[a_y][a_x]
    b = image[a_y+1][a_x]
    c = image[a_y][a_x+1]
    d = image[a_y+1][a_x+1]
    delta_x = abs(x-a_x)
    delta_y = abs(y-a_y)
    pixel = round(a*(1-delta_x)*(1-delta_y)+b*delta_y *
                  (1-delta_x)+c*delta_x*(1-delta_y)+d*delta_x*delta_y)
    if pixel < 0:
        pixel = 0
    if pixel > 255:
        pixel = 255
    return pixel

# gets a image and scales for a new one and creates the resizes picture


def resize(image: SingleChannelImage, new_height: int, new_width: int) -> SingleChannelImage:
    new_image = []
    for rows in range(new_height):
        current_row = []
        for columns in range(new_width):
            current_row.append(bilinear_interpolation(
                image, (rows/(new_height-1))*(len(image)-1), (columns/(new_width-1))*(len(image[0])-1)))
        new_image.append(current_row)
    return new_image

# gets a picture and return a rotated version


def rotate_90(image: Image, direction: str) -> Image:
    rotated_image = []
    num_column = len(image[0])
    for columns in range(num_column):
        if direction == 'R':
            rotated_image.append([current_row[columns]
                                 for current_row in image[::-1]])
        else:
            rotated_image.append([current_row[num_column-1-columns]
                                 for current_row in image])
    return rotated_image

# gets an image and and return an edged version


def get_edges(image: SingleChannelImage, blur_size: int, block_size: int, c: float) -> SingleChannelImage:
    mid_bloc = block_size//2
    kernel = blur_kernel(blur_size)
    blurred_image = apply_kernel(image, kernel)
    edged_image = []
    num_rows = len(blurred_image)
    num_columns = len(blurred_image[0])
    for row in range(num_rows):
        edged_row = []
        for column in range(num_columns):
            sum = 0
            for a in range(block_size):
                for b in range(block_size):
                    if row-mid_bloc+a < 0 or row-mid_bloc+a > num_rows-1 or column-mid_bloc+b < 0 or column-mid_bloc+b > num_columns-1:
                        sum += blurred_image[row][column]
                    else:
                        sum += blurred_image[row -
                                             mid_bloc+a][column - mid_bloc+b]
            if blurred_image[row][column] < (sum/(block_size**2))-c:
                edged_row.append(0)
            else:
                edged_row.append(255)
        edged_image.append(edged_row)
    return edged_image

# gets a grey image and return a picture with less color shades


def quantize(image: SingleChannelImage, N: int) -> SingleChannelImage:
    quantized_image = []
    num_rows = len(image)
    num_columns = len(image[0])
    for row in range(num_rows):
        quantized_row = []
        for column in range(num_columns):
            quantized_row.append(
                round((math.floor(image[row][column]*(N/256)))*(255/(N-1))))
        quantized_image.append(quantized_row)
    return quantized_image

# gets an colored image and return a picture with less color shades


def quantize_colored_image(image: ColoredImage, N: int) -> ColoredImage:
    q_c_image = separate_channels(image)
    q_rows = []
    for row in q_c_image:
        q_rows.append(quantize(row, N))
    q_c_image = combine_channels(q_rows)
    return q_c_image

# gets an image and convert it to grey


def answer_1(image):
    if isinstance(image[0][0], list):
        new_image = RGB2grayscale(image)
        return new_image
    else:
        print("your image is already gray")
        return image

# gets an image and return a blurred image


def answer_2(image):
    a = input("enter the size of the blurring kernel : ")
    if a.isnumeric() and int(a) > 0 and int(a) % 2:
        if isinstance(image[0][0], list):
            new_image = separate_channels(image)
            row_image = []
            for row in new_image:
                row_image.append(apply_kernel(
                    row, blur_kernel(int(a))))
            new_image = combine_channels(row_image)
            return new_image
        else:
            new_image = apply_kernel(new_image, blur_kernel(int(a)))
            return new_image
    else:
        print('the number has to be an integer, positive and odd')
        return image

# resize image


def answer_3(image):
    a = input("choose height and width seperated by comma for the new image : ")
    if ',' in a:
        a = a.split(',')
        if len(a) == 2 and a[0].isnumeric() and a[1].isnumeric() and int(a[0]) > 1 and int(a[1]) > 1:
            if isinstance(image[0][0], list):
                new_image = separate_channels(image)
                row_image = []
                for row in new_image:
                    row_image.append(resize(row, int(a[0]), int(a[1])))
                new_image = combine_channels(row_image)
                return new_image
            else:
                new_image = resize(image, int(a[0]), int(a[1]))
                return new_image
        else:
            print("the width and height must be bigger then 1")
            return image
    else:
        print("the width and height must be bigger then 1")
        return image

# rotate image


def answer_4(image):
    a = input(" choose R or left : ")
    if a == 'R':
        new_image = rotate_90(image, 'R')
        return new_image
    elif a == 'L':
        new_image = rotate_90(image, 'L')
        return new_image
    else:
        print("invalid input")
        return image

# create an edged image


def answer_5(image):
    a = input("enter blur size, block size and a c : ")
    if ',' in a:
        a = a.split(',')
        if len(a) == 3 and a[0].isnumeric() and a[1].isnumeric() and a[2].isnumeric() and int(a[0]) > 0 and int(a[0]) % 2 and int(a[1]) > 0 and int(a[1]) % 2 and int(a[2]) >= 0:
            if isinstance(image[0][0], list):
                new_image = separate_channels(image)
                row_image = []
                for row in new_image:
                    row_image.append(
                        get_edges(row, int(a[0]), int(a[1]), int(a[2])))
                new_image = combine_channels(row_image)
                return new_image
            else:
                new_image = get_edges(
                    get_edges(image, int(a[0]), int(a[1]), int(a[2])))
                return new_image
        else:
            print("the first two must be integer, positive and odd, and c must be non negative integer. every number seperated by comma")
            return image
    else:
        print("the first two must be integer, positive and odd, and c must be non negative integer. every number seperated by comma")
        return image

# quantize image


def answer_6(image):
    a = input("choose number of shades : ")
    if a.isnumeric() and int(a) > 1:
        if isinstance(image[0][0], list):
            new_image = quantize_colored_image(image, int(a))
            return new_image
        else:
            new_image = quantize(image, int(a))
            return new_image
    else:
        print("invalid input")
        return image


if __name__ == '__main__':
    if len(sys.argv) == 2:
        source_image = load_image(sys.argv[1])
        new_image = copy.deepcopy(source_image)
        answer = input(
            "1 - convert image to grayscale\n2 - blur image\n3 - resize image\n4 - rotate image\n5 - creates an edged image\n6 - quantize image\n7 - show image\n8 - exit\n")
        while answer != '8':
            if answer == '1':
                new_image = answer_1(new_image)
            elif answer == '2':
                new_image = answer_2(new_image)
            elif answer == '3':
                new_image = answer_3(new_image)
            elif answer == '4':
                new_image = answer_4(new_image)
            elif answer == '5':
                new_image = answer_5(new_image)
            elif answer == '6':
                new_image = answer_6(new_image)
            elif answer == '7':
                show_image(new_image)
            else:
                print("invalid input")
            answer = input(
                "1 - convert image to grayscale\n2 - blur image\n3 - resize image\n4 - rotate image\n5 - creates an edged image\n6 - quantize image\n7 - show image\n8 - exit\n")
        a = input("enter a saving path : ")
        save_image(new_image, a)
    else:
        print("invalid arguments")

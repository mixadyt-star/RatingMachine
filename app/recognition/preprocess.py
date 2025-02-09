from cv2.typing import MatLike
from typing import List
import cv2
import numpy as np

import config

def find_table(image: MatLike) -> MatLike | None:
    '''
    Takes photo returns contour of table
    '''

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh_image = cv2.adaptiveThreshold(gray_image, 255,
                                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY_INV, 11, 2)
    
    cnts, _ = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(cnts, key = cv2.contourArea) if cnts else None
    
    return max_contour

def crop_table(image: MatLike, contour: MatLike) -> MatLike | None:
    '''
    Takes photo and contour returns image of table
    '''

    if contour is not None:
        x, y, w, h = cv2.boundingRect(contour)
        table_image = image[y:y + h, x:x + w]

        return table_image
    return None

def find_cells(table_image: MatLike) -> List[MatLike]:
    '''
    Takes table photo and returns contours of cells
    '''

    gray_table = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
    threshholded_table = cv2.adaptiveThreshold(gray_table, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 57, 5)

    table_cnts = cv2.findContours(threshholded_table, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    table_cnts = table_cnts[0] if len(table_cnts) == 2 else table_cnts[1]

    inverted_table = 255 - threshholded_table
    cells_cnts = cv2.findContours(inverted_table, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cells_cnts = cells_cnts[0] if len(cells_cnts) == 2 else cells_cnts[1]

    cells = []

    for cnt in cells_cnts:
        tmp = table_image.copy()
        
        _, _, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)

        if w <= config.MAX_CELL_WIDTH and h <= config.MAX_CELL_HEIGHT and area > config.MIN_CELL_AREA and w >= config.MIN_CELL_WIDTH:
            cells.append(cnt)
    
    return cells

def crop_cells(table_image: MatLike, contours: List[MatLike]) -> List[MatLike]:
    '''
    Takes table photo and cell contours returns cell images
    '''
    
    cells = []
    for cnt in contours:
        mask = np.zeros(table_image.shape, dtype = np.uint8)
        cv2.drawContours(mask, [cnt], -1, (255, 255, 255), -1)
        cell = cv2.bitwise_and(table_image, mask)

        x, y, w, h = cv2.boundingRect(cnt)
        black_background = np.zeros((h, w, 3), dtype=np.uint8)
        black_background[:] = (0, 0, 0)
        black_background[:cell.shape[0], :cell.shape[1]] = cell[y:y + h, x:x + w]

        cells.append(black_background)
    
    return cells


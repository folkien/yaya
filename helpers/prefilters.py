"""
Created on 18 lis 2020

@author: spasz
"""

import numpy as np

from engine.annote import Annote

from helpers.boxes import iou


def filter_iou_by_confidence(
    annotations1: list[Annote], annotations2: list[Annote], maxIOU: float = 0.70
) -> list[Annote]:
    """
    Filter annotation1 with annotations2
    if has bigger IOU > maxIOU.
    Annotation with bigger confidence stays!
    """

    # Create IOU results matrix
    results = np.zeros([len(annotations1), len(annotations2)], dtype=np.float32)
    for i, annote1 in enumerate(annotations1):
        for j, annote2 in enumerate(annotations2):
            if annote1 != annote2:
                results[i, j] = iou(annote1.GetBox(), annote2.GetBox())

    # Parse each row of IOU matrix
    passed: list[Annote] = []
    for i, annote in enumerate(annotations1):
        isFiltered = False

        # For every other annotation
        for j in range(len(annotations2)):
            # If (IOU >= maxIOU) and confidence is smaller
            if (results[i, j] >= maxIOU) and (
                annote.GetConfidence() <= annotations2[j].GetConfidence()
            ):
                isFiltered = True
                # Affect annotations_2 confidence
                annotations2[j].confidence = annote.confidence
                break

        # Check : Filtered, then skip adding
        if isFiltered is True:
            continue

        # If not filtered, add to passed list
        passed.append(annote)

    return passed

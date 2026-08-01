# kmeans.py

import numpy as np
import random


def init_centroids(K, image):
    """
    Randomly initialize K centroids from the image pixels.
    """
    height, width, channels = image.shape

    centroids = np.empty((K, channels))

    for i in range(K):
        rand_row = random.randint(0, height - 1)
        rand_col = random.randint(0, width - 1)
        centroids[i] = image[rand_row, rand_col]

    return centroids


def find_closest_centroid(pixel, centroids):
    """
    Find the index of the nearest centroid.
    """
    distances = np.linalg.norm(centroids - pixel, axis=1)
    return np.argmin(distances)


# def assign_clusters(image, centroids):
#     """
#     Assign every pixel in the image to its nearest centroid.
#     """
#     height, width, channels = image.shape

#     labels = np.zeros((height, width), dtype=np.int32)

#     for i in range(height):
#         for j in range(width):
#             labels[i, j] = find_closest_centroid(image[i, j], centroids)

#     return labels

def assign_clusters(image, centroids):
    """
    Assign every pixel to its nearest centroid using vectorized NumPy operations.
    """

    height, width, channels = image.shape

    # Convert image to (num_pixels, 3)
    pixels = image.reshape(-1, channels)

    # Compute distance from every pixel to every centroid
    distances = np.linalg.norm(
        pixels[:, np.newaxis] - centroids,
        axis=2
    )

    # Find nearest centroid
    labels = np.argmin(distances, axis=1)

    # Convert back to image shape
    labels = labels.reshape(height, width)

    return labels


def update_centroids(image, labels, K):
    """
    Update centroid values by taking the mean of all
    pixels assigned to each cluster.
    """
    height, width, channels = image.shape

    new_centroids = np.zeros((K, channels))

    for k in range(K):

        pixels = image[labels == k]

        if len(pixels) > 0:
            new_centroids[k] = np.mean(pixels, axis=0)

    return new_centroids


def kmeans(image, K, max_iters=20, tolerance=1e-4, return_info=False):
    """
    Run the K-Means clustering algorithm.
    """
    centroids = init_centroids(K, image)
    iterations = 0
    converged = False

    for i in range(max_iters):

        labels = assign_clusters(image, centroids)

        new_centroids = update_centroids(image, labels, K)
        iterations = i + 1

        if np.allclose(centroids, new_centroids, atol=tolerance):
            centroids = new_centroids
            converged = True
            break

        centroids = new_centroids

    if return_info:
        return centroids, labels, {
            "iterations": iterations,
            "converged": converged,
            "tolerance": tolerance,
        }

    return centroids, labels


def compress_image(labels, centroids):
    """
    Replace every pixel with its corresponding centroid color.
    """
    compressed_image = centroids[labels]
    return compressed_image
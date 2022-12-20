#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  19 16:51:11 2022

@author: Jonho
"""

from google.cloud import storage
        
# The ID of your GCS bucket
# bucket_name = "your-bucket-name"
bucket_name = 'bucket-horseracing-results-pdfs'



def authenticate_implicit_with_adc(project_id="horse-racing-analytics"):
    # Note that the credentials are not specified when constructing the client.
    # Hence, the client library will look for credentials using ADC.
    storage_client = storage.Client(project=project_id)
    print("Authenticated")


def download_pdf(source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client("horse-racing-analytics")

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name)
        )
        
def list_pdfs():
    """Lists all the blobs in the bucket."""
    bucket_name = "bucket-horseracing-results-pdfs"

    storage_client = storage.Client("horse-racing-analytics")

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    # Note: The call returns a response only when the iterator is consumed.
    pdf_list = []
    for blob in blobs:
        print(blob.name)
        pdf_list.append(blob.name)
    return pdf_list




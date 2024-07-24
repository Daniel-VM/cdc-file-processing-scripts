"""
    emm_donwload_makedb.py

This script downloads and processes .sds files from a specified remote FTP server directory.
It filters for emm-specific .sds files, downloads them to a local directory, and converts their
content into FASTA format.

Credits:
This script was developed by Daniel-VM (https://github.com/Daniel-VM)

"""
# TODO: make a requirements.txt (requests, bs4, )
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import argparse
from datetime import datetime
import subprocess

def download_and_process_sds_files(ftp_url, remote_path, local_path):
    # List all files in the remote directory
    response = requests.get(ftp_url + remote_path)
    html_content = response.text
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <a> tags containing the file names
    links = soup.find_all('a')

    # Extract file names from the <a> tags
    ftp_files = [link['href'] for link in links if link['href'].endswith('.sds')]
    
    # Filter for SDS files
    sds_files = [os.path.basename(filename) for filename in ftp_files if filename.endswith('.sds')]
    # Filter by emm specific files
    sds_emm_files = [emm_file for emm_file in sds_files if emm_file.startswith('emm')]
    sds_emm_files = sds_emm_files[0:5]

    # List to store all fasta sequences
    all_fasta_sequences = []
    
    # Iterate through each SDS file
    for sds_file in sds_emm_files:
        print(f'Processing file: {sds_file}')
        # Download the SDS file
        remote_file = f"{ftp_url}/{remote_path}/{sds_file}"
        local_file = os.path.join(local_path, sds_file)
        response = requests.get(remote_file)

        # Write the content to the local file
        with open(local_file, 'wb') as f:
            f.write(response.content)

        # Generate the FASTA sequence from the SDS file
        fasta_seq = generate_fasta_sequence(local_file, sds_file)

        # Write the FASTA sequence to a file
        fasta_filename = os.path.splitext(local_file)[0] + '.fasta'
        with open(fasta_filename, 'w') as fasta_file:
            fasta_file.write(fasta_seq)
        
        # Append the fasta sequence to the list
        all_fasta_sequences.append(fasta_seq)

    # Write all fasta sequences to a single multi-FASTA file
    current_date = datetime.now().strftime('%d%m%Y')
    multifasta_filename = f"cdc_emm_database{current_date}.fasta"
    multifasta_path = os.path.join(local_path, multifasta_filename)

    with open(multifasta_path, 'w') as multifasta_file:
        for fasta_seq in all_fasta_sequences:
            multifasta_file.write(fasta_seq)
    return multifasta_filename


def generate_fasta_sequence(sds_file_path, sds_file_name):
    # Read the content of the SDS file
    with open(sds_file_path, 'r') as sds_file:
        sds_file_lines = sds_file.readlines()
    
    # Pattern to match lines with nucleotide sequences
    nucleotide_pattern = r'^\s*\d+\s+[ACGTactg\s-]+\s*$'

    # Filter lines containing nucleotide sequences
    nucleotide_items = [line.strip().split()[1:] for line in sds_file_lines if re.findall(nucleotide_pattern, line)]

    # Concatenate the sequences
    concatenated_sequence = ''.join([sequence for sublist in nucleotide_items for sequence in sublist])

    # Generate the sequence identifier for the FASTA file
    # FIXME: Tag 'CDC_2024_TSEEM_EMM_DATABASE' is harcoded.
    emm_id = sds_file_name.split('.sds')[0]
    sequence_id = f">{emm_id.upper()} {sds_file_name} CDC_2024_TSEEM_EMM_DATABASE"

    # Construct the FASTA sequence
    fasta_sequence = f"{sequence_id}\n{concatenated_sequence.upper()}\n"
    print(fasta_sequence)

    return fasta_sequence

def run_makedatabase_blast(fasta_file):
    # Check if makeblastdb is installed
    db_name = os.path.basename(fasta_file)
    try:
        subprocess.run(['makeblastdb', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"makeblastdb is not installed. Please install BLAST+ to proceed.{e}")
        sys.exit(1)
    
    # Run the makeblastdb command
    try:
        subprocess.run(['makeblastdb', '-in', fasta_file, '-dbtype', 'nucl', '-out', db_name], check=True)
        print(f"Database created successfully: {db_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating BLAST database: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Download and process (and make BLAST database) of emm-SDS files from an FTP server.')
    parser.add_argument('--ftp_url', required=True, help='FTP URL')
    parser.add_argument('--remote_path', required=True, help='Remote path on the FTP server')
    parser.add_argument('--local_path', required=True, help='Local path to save the downloaded files')
    parser.add_argument('--make_blastdb', action='store_true', help='Create a database with BLAST')
    parser.add_argument('--db_name', required=False, help='Name of the BLAST database')
    
    args = parser.parse_args()

    # Download and process emm sequences
    emm_multifasta_file = download_and_process_sds_files(args.ftp_url, args.remote_path, args.local_path)

    # Make blastdb
    if args.make_blastdb:
        if not args.db_name:
            print("Database name is required when make_blastdb is set to True.")
            #sys.exit(1)
        run_makedatabase_blast(emm_multifasta_file)

if __name__ == '__main__':
    main()

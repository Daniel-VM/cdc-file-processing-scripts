# cdc-file-processing-scripts

## `emm_download_makedb.py`

This script is designed to download and process SDS files from a specified FTP server, extract FASTA sequences from these files, and optionally create a BLAST database from the processed sequences. The script is particularly tailored for handling emm gene data from the CDC's TSEEM database.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python >= 3.9
- `requests` library
- `beautifulsoup4` library
- BLAST+ 2.16.0 (for creating BLAST databases) ([Bioconda](https://anaconda.org/bioconda/blast))

You can install these dependencies via conda: the necessary Python libraries using pip:

```sh
pip install requests beautifulsoup4

```

### Arguments

```
usage: emm_download_makedb.py [-h] --ftp_url FTP_URL --remote_path REMOTE_PATH --local_path LOCAL_PATH [--make_blastdb] [--db_name DB_NAME]

Download and process (and make BLAST database) of emm-SDS files from an FTP server.

options:
  -h, --help            show this help message and exit
  --ftp_url FTP_URL     FTP URL
  --remote_path REMOTE_PATH
                        Remote path on the FTP server
  --local_path LOCAL_PATH
                        Local path to save the downloaded files
  --make_blastdb        Create a database with BLAST
  --db_name DB_NAME     Name of the BLAST database (opional)
```


### Usage

```
python emm_download_makedb.py \
    --ftp_url 'https://ftp.cdc.gov/' \
    --remote_path 'pub/infectious_diseases/biotech/tsemm/' \
    --local_path ./out_fasta \
    --make_blastdb \
    --db_name blast_database
```

This command will:

1. Download SDS files from the specified FTP URL and remote path.
2. Save the downloaded files in the specified local path.
3. Process the SDS files to extract FASTA sequences.
4. Save all FASTA sequences into a single multi-FASTA file.
5. If the `--make_blastdb` flag is set, create a BLAST database from the multi-FASTA file with the specified database name.

### Output
- FASTA Files: SDS files are processed into individual FASTA files, each named after the corresponding SDS file.

- Multi-FASTA File: All individual FASTA sequences are concatenated into a single multi-FASTA file, saved at the path specified by --multifasta_path.

- BLAST Database: If the --make_blastdb flag is used, a BLAST database is created from the multi-FASTA file and saved with the name specified by --db_name.

### Extension

The generated BLAST database can now be used as input for tools such as emmtyper. Here’s an example command to use the created BLAST database with emmtyper:

```sh
emmtyper \
        -w blast \
        --keep  \
        --blast_db 'path_to_blastdb/CDC_2024_TSEEM_EMM_DATABASE' \
        --percent-identity 95 \
        --culling-limit 5 \
        --output results.out \
        --output-format verbose \
        'path_to/input_fasta_files.fasta'
```
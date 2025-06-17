# bwell_logmerger

A Python tool for merging multiple JSON log files from the National Research Council's [bWell](https://nrc.canada.ca/en/research-development/products-services/technical-advisory-services/bwell) platform into a single consolidated log file.

## Description

This tool merges log records from multiple JSON files while preserving the original schema structure. The merged output maintains metadata information about the source files and supports recursive merging (merging already-merged files).

## Usage

### Basic Usage

```bash
python log_merger.py -i file1.json file2.json -o merged_output.json
```

### Options

- `-i, --input`: Input JSON log files to merge (minimum 2 files required)
- `-o, --output`: Output file path for the merged log
- `--pretty`: Pretty print the output JSON with indentation
- `--verbose`: Enable verbose output showing merge details

### Examples

Merge two log files:
```bash
python log_merger.py -i log1.json log2.json -o merged.json
```

Merge multiple files with pretty formatting:
```bash
python log_merger.py -i log1.json log2.json log3.json -o merged.json --pretty
```

## Input Format

Input files should follow the bWell log format with *at least* the following required fields:
- `data`: Array of log records

## Output Format

The merged output maintains the same schema as input files with additional metadata:
- `merged_sources`: Information about source files and merge history
  - `merged_at`: Timestamp of merge operation
  - `base_file`: The primary file used as the base
  - `additional_files`: List of additional files merged in
  - `total_files_merged`: Total number of files in the merge
  - `previous_merges`: History of previous merge operations (for recursive merges)

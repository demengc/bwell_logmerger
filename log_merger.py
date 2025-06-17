"""
Merges multiple bWell JSON log files into a single file.
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {filepath}: {e}")
    except Exception as e:
        raise Exception(f"Error reading file {filepath}: {e}")


def is_merged_file(log_data: Dict[str, Any]) -> bool:
    """Check if a log file is already a merged file."""
    return "merged_sources" in log_data


def create_merged_metadata(base_file: str, additional_files: List[str], base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create metadata for a merged log file."""
    merged_info = {
        "merged_at": datetime.now().isoformat(),
        "base_file": base_file,
        "additional_files": additional_files,
        "total_files_merged": len(additional_files) + 1
    }
    
    # If base file is already merged, extend the metadata
    if is_merged_file(base_data):
        existing_sources = base_data.get("merged_sources", {})
        merged_info["base_file"] = existing_sources.get("base_file", base_file)
        merged_info["additional_files"] = existing_sources.get("additional_files", []) + additional_files
        merged_info["total_files_merged"] = len(merged_info["additional_files"]) + 1
        
        # Track previous merge information
        merged_info["previous_merges"] = existing_sources.get("previous_merges", [])
        merged_info["previous_merges"].append({
            "merged_at": existing_sources.get("merged_at"),
            "files_in_merge": [existing_sources.get("base_file")] + existing_sources.get("additional_files", [])
        })
    
    return merged_info


def merge_log_files(file_paths: List[str]) -> Dict[str, Any]:
    """
    Merge multiple bWell log files.
    
    Args:
        file_paths: List of paths to JSON log files to merge
        
    Returns:
        Dict containing the merged log data
    """
    if len(file_paths) < 2:
        raise ValueError("At least 2 files are required for merging")
    
    log_data_list = []
    for filepath in file_paths:
        log_data = load_json_file(filepath)
        log_data_list.append((filepath, log_data))
    
    base_filepath, base_data = log_data_list[0]
    
    for filepath, log_data in log_data_list:
        if "data" not in log_data:
            raise ValueError(f"File {filepath} is missing required 'data' field")
        if not isinstance(log_data["data"], list):
            raise ValueError(f"File {filepath} 'data' field must be a list")
    
    merged_result = base_data.copy()
    
    all_data_records = []
    all_data_records.extend(base_data["data"])
    
    additional_files = []
    for filepath, log_data in log_data_list[1:]:
        additional_files.append(filepath)
        all_data_records.extend(log_data["data"])
    
    # Sort data records by timestamp if available
    def get_timestamp(record):
        return record.get("timestamp", 0)
    
    try:
        all_data_records.sort(key=get_timestamp)
    except (TypeError, KeyError):
        pass
    
    merged_result["data"] = all_data_records
    
    merged_sources = create_merged_metadata(base_filepath, additional_files, base_data)
    merged_result["merged_sources"] = merged_sources
    
    return merged_result


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Merge multiple bWell JSON log files"
    )
    
    parser.add_argument(
        "-i", "--input",
        nargs="+",
        required=True,
        help="Input JSON log files to merge (minimum 2 files)"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path for the merged log"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print the output JSON with indentation"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        for filepath in args.input:
            if not Path(filepath).exists():
                print(f"Error: File not found: {filepath}", file=sys.stderr)
                sys.exit(1)
        
        if args.verbose:
            print(f"Merging {len(args.input)} files...")
            for filepath in args.input:
                print(f"  - {filepath}")
        
        merged_data = merge_log_files(args.input)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.pretty:
                json.dump(merged_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(merged_data, f, ensure_ascii=False)
        
        if args.verbose:
            total_records = len(merged_data["data"])
            print(f"Successfully merged {len(args.input)} files into {args.output}")
            print(f"Total data records: {total_records}")
            
            merged_sources = merged_data.get("merged_sources", {})
            print(f"Base file: {merged_sources.get('base_file', 'N/A')}")
            print(f"Additional files: {len(merged_sources.get('additional_files', []))}")
        else:
            print(f"Merged {len(args.input)} files into {args.output}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

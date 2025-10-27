#!/usr/bin/env python3
"""
Asset Folder Analyzer - Standalone tool to scan and analyze asset folder structures

This tool scans a folder containing 3D assets and textures, automatically identifying:
- Main assets vs variants (files with _B, _C suffixes)
- Texture folders prioritized by resolution (4k > 2k > 1k)

Can be used standalone from command line or imported as a module.

Usage:
    # Command line
    python asset_folder_analyzer.py /path/to/assets

    # As a module
    from tools.asset_folder_analyzer import analyze_asset_folder
    result = analyze_asset_folder("/path/to/assets")
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for module imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from modules.asset_folder_scanner import AssetFolderScanner, scan_asset_folder


def analyze_asset_folder(root_path, geo_subfolder="geo", tex_subfolder="tex", output_format="dict"):
    """
    Analyze an asset folder and return structured results.

    Args:
        root_path (str): Path to root folder containing assets
        geo_subfolder (str): Name of geometry subfolder (default: "geo")
        tex_subfolder (str): Name of texture subfolder (default: "tex")
        output_format (str): Output format - "dict", "json", or "summary" (default: "dict")

    Returns:
        dict|str: Analysis results in requested format
    """
    try:
        scanner = AssetFolderScanner(root_path)
        result = scanner.scan_folder(geo_subfolder, tex_subfolder)

        if output_format == "json":
            return json.dumps(result, indent=2)
        elif output_format == "summary":
            return _format_summary(result)
        else:
            return result

    except Exception as e:
        return {"error": str(e)}


def _format_summary(result):
    """
    Format scan results as a human-readable summary.

    Args:
        result (dict): Scan results from scanner

    Returns:
        str: Formatted summary text
    """
    lines = []
    lines.append("=" * 70)
    lines.append("ASSET FOLDER ANALYSIS")
    lines.append("=" * 70)

    # Errors
    if result.get('errors'):
        lines.append("\n⚠️  ERRORS:")
        for error in result['errors']:
            lines.append(f"  - {error}")

    # Geometry Files
    lines.append("\n📦 GEOMETRY FILES:")
    if result.get('main_asset'):
        lines.append(f"  Main Asset: {os.path.basename(result['main_asset'])}")
        lines.append(f"    Path: {result['main_asset']}")
    else:
        lines.append("  Main Asset: None found")

    if result.get('asset_variants'):
        lines.append(f"\n  Variants ({len(result['asset_variants'])}):")
        for variant in result['asset_variants']:
            lines.append(f"    - {os.path.basename(variant)}")
    else:
        lines.append("\n  Variants: None")

    # Geometry file details
    if result.get('geometry_files'):
        lines.append(f"\n  All Geometry Files ({len(result['geometry_files'])}):")
        for name, info in sorted(result['geometry_files'].items()):
            variant_tag = " [VARIANT]" if info['is_variant'] else " [MAIN]"
            lines.append(f"    - {info['filename']}{variant_tag}")
            lines.append(f"      Extension: {info['extension']}")

    # Texture Folders
    lines.append("\n🎨 TEXTURE FOLDERS:")
    if result.get('main_textures'):
        lines.append(f"  Main Textures: {os.path.basename(result['main_textures'])}")
        lines.append(f"    Path: {result['main_textures']}")

        # Find resolution info
        if result.get('texture_folders'):
            for path, info in result['texture_folders'].items():
                if path == result['main_textures']:
                    res_str = info['resolution'] if info['resolution'] else "unknown"
                    lines.append(f"    Resolution: {res_str}")
                    lines.append(f"    Texture Count: {info['texture_count']}")
                    break
    else:
        lines.append("  Main Textures: None found")

    if result.get('material_variants'):
        lines.append(f"\n  Material Variants ({len(result['material_variants'])}):")
        for variant_path in result['material_variants']:
            folder_name = os.path.basename(variant_path)
            lines.append(f"    - {folder_name}")

            # Find resolution info
            if result.get('texture_folders'):
                for path, info in result['texture_folders'].items():
                    if path == variant_path:
                        res_str = info['resolution'] if info['resolution'] else "unknown"
                        lines.append(f"      Resolution: {res_str}, Textures: {info['texture_count']}")
                        break
    else:
        lines.append("\n  Material Variants: None")

    # All texture folders with details
    if result.get('texture_folders'):
        lines.append(f"\n  All Texture Folders ({len(result['texture_folders'])}):")
        sorted_folders = sorted(
            result['texture_folders'].items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        )
        for path, info in sorted_folders:
            res_str = info['resolution'] if info['resolution'] else "unknown"
            priority_str = f"[Priority: {info['priority']}]"
            lines.append(f"    - {info['name']} {priority_str}")
            lines.append(f"      Resolution: {res_str}, Textures: {info['texture_count']}")
            lines.append(f"      Path: {info['relative_path']}")

    # Summary statistics
    lines.append("\n" + "=" * 70)
    lines.append("SUMMARY:")
    lines.append(f"  Total Geometry Files: {len(result.get('geometry_files', {}))}")
    lines.append(f"  Total Texture Folders: {len(result.get('texture_folders', {}))}")

    if result.get('main_asset'):
        lines.append(f"  ✓ Ready for LOPS Asset Builder")
    else:
        lines.append(f"  ⚠️  Missing main asset")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Analyze asset folder structure for LOPS Asset Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze folder with default subfolders (geo, tex)
  python asset_folder_analyzer.py /path/to/assets

  # Specify custom subfolder names
  python asset_folder_analyzer.py /path/to/assets --geo models --tex textures

  # Output as JSON
  python asset_folder_analyzer.py /path/to/assets --format json

  # Output detailed summary (default)
  python asset_folder_analyzer.py /path/to/assets --format summary

  # Save output to file
  python asset_folder_analyzer.py /path/to/assets --output report.txt
        """
    )

    parser.add_argument(
        'path',
        help='Path to the root asset folder to analyze'
    )

    parser.add_argument(
        '--geo',
        default='geo',
        help='Name of geometry subfolder (default: geo)'
    )

    parser.add_argument(
        '--tex',
        default='tex',
        help='Name of texture subfolder (default: tex)'
    )

    parser.add_argument(
        '--format',
        choices=['summary', 'json', 'dict'],
        default='summary',
        help='Output format (default: summary)'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Output file path (prints to stdout if not specified)'
    )

    args = parser.parse_args()

    # Validate path
    if not os.path.exists(args.path):
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Analyze folder
    result = analyze_asset_folder(
        args.path,
        geo_subfolder=args.geo,
        tex_subfolder=args.tex,
        output_format=args.format
    )

    # Format output
    if args.format == 'dict':
        import pprint
        output = pprint.pformat(result, width=120)
    else:
        output = result

    # Write to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Analysis written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()

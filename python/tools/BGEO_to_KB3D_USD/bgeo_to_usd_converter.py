"""
BGEO to USD Converter - Main orchestrator for BGEO to KB3D USD conversion

This module coordinates the entire conversion process:
1. Analyze BGEO files
2. Group by assets and parts
3. Create component USDs
4. Create assembly USDs
5. Handle material references

Author: Custom Tools
Date: 2025-10-28
"""

import os
from typing import Dict, List, Optional
from collections import defaultdict

from .bgeo_analyzer import BGEOAnalyzer
from .usd_component_builder import USDComponentBuilder
from .usd_assembly_builder import USDAssemblyBuilder


class BGEOtoUSDConverter:
    """Main converter class for BGEO to KB3D USD conversion."""

    def __init__(self):
        self.analyzer = BGEOAnalyzer()
        self.component_builder = USDComponentBuilder()
        self.assembly_builder = USDAssemblyBuilder()

        self.default_kit_info = {
            'kitDisplayName': 'Custom Assets',
            'kitId': 'custom_assets',
            'kitVersion': '1.0.0'
        }

    def convert(
        self,
        bgeo_folder: str,
        output_folder: str,
        kit_info: Optional[Dict] = None,
        texture_variants: Optional[List[str]] = None,
        default_variant: str = 'png4k',
        create_assemblies: bool = True,
        bgeo_pattern: str = '*.bgeo.sc'
    ) -> Dict:
        """
        Convert all BGEO files in folder to KB3D USD structure.

        Args:
            bgeo_folder: Folder containing BGEO.SC files
            output_folder: Root output folder for USD files
            kit_info: KB3D metadata
            texture_variants: List of texture variants
            default_variant: Default texture variant
            create_assemblies: Create assembly USDs (True) or only components (False)
            bgeo_pattern: File pattern for BGEO files

        Returns:
            {
                'success': bool,
                'components': list of created components,
                'assemblies': list of created assemblies,
                'materials': set of all materials found,
                'errors': list of errors,
                'summary': text summary
            }
        """
        # Set defaults
        if kit_info is None:
            kit_info = self.default_kit_info.copy()

        if texture_variants is None:
            texture_variants = ['jpg1k', 'jpg2k', 'jpg4k', 'png1k', 'png2k', 'png4k']

        # Step 1: Analyze BGEO files
        print("Step 1: Analyzing BGEO files...")
        analysis = self.analyzer.analyze_folder(bgeo_folder, bgeo_pattern)

        if not analysis['success']:
            return {
                'success': False,
                'error': analysis.get('error', 'Analysis failed'),
                'components': [],
                'assemblies': [],
                'materials': set(),
                'errors': analysis.get('errors', [])
            }

        print(f"  Found {len(analysis['assets'])} assets")
        print(self.analyzer.get_asset_summary(analysis['assets']))

        # Prepare output
        components_created = []
        assemblies_created = []
        all_materials = set()
        errors = []

        # Step 2: Create component USDs for each part
        print("\nStep 2: Creating component USDs...")

        for asset_name, asset_data in analysis['assets'].items():
            print(f"\n  Processing asset: {asset_name}")

            # Determine if this is a single component or assembly with multiple parts
            parts = asset_data['parts']

            if len(parts) == 1 and create_assemblies is False:
                # Single component - create directly
                part_name = list(parts.keys())[0]
                part_data = parts[part_name]

                component_name = asset_name
                component_folder = os.path.join(output_folder, 'Models', component_name)

                print(f"    Creating single component: {component_name}")

                result = self.component_builder.create_component(
                    component_name=component_name,
                    geometry=part_data['geometry'],
                    output_folder=component_folder,
                    materials=part_data['materials'],
                    kit_info=kit_info,
                    texture_variants=texture_variants,
                    default_variant=default_variant,
                    kind='component'
                )

                if result['success']:
                    components_created.append(result)
                    all_materials.update(part_data['materials'])
                else:
                    errors.append(result.get('error', 'Unknown error'))

            else:
                # Multiple parts or assembly requested
                # Create individual component USDs for each part
                component_refs = []

                for part_name, part_data in parts.items():
                    component_name = f"{asset_name}_{part_name}"
                    component_folder = os.path.join(output_folder, 'Models', component_name)

                    print(f"    Creating component: {component_name}")

                    result = self.component_builder.create_component(
                        component_name=component_name,
                        geometry=part_data['geometry'],
                        output_folder=component_folder,
                        materials=part_data['materials'],
                        kit_info=kit_info,
                        texture_variants=texture_variants,
                        default_variant=default_variant,
                        kind='component'
                    )

                    if result['success']:
                        components_created.append(result)
                        all_materials.update(part_data['materials'])

                        # Store for assembly creation
                        component_refs.append({
                            'name': f"{asset_name}_{part_name}_001",  # Instance name
                            'reference': f"../{component_name}/{component_name}.usd",
                            'component_name': component_name,
                            'kind': 'component',
                            'instanceable': True
                            # TODO: Extract transforms from BGEO if available
                        })
                    else:
                        errors.append(result.get('error', 'Unknown error'))

                # Step 3: Create assembly USD if requested
                if create_assemblies and component_refs:
                    print(f"\n  Creating assembly: {asset_name}")
                    assembly_folder = os.path.join(output_folder, 'Models', asset_name)

                    assembly_result = self.assembly_builder.create_assembly(
                        assembly_name=asset_name,
                        components=component_refs,
                        output_folder=assembly_folder,
                        kit_info=kit_info,
                        texture_variants=texture_variants,
                        default_variant=default_variant
                    )

                    if assembly_result['success']:
                        assemblies_created.append(assembly_result)
                    else:
                        errors.append(assembly_result.get('error', 'Unknown error'))

        # Generate summary
        summary_lines = [
            "="*60,
            "BGEO TO USD CONVERSION SUMMARY",
            "="*60,
            f"Components created: {len(components_created)}",
            f"Assemblies created: {len(assemblies_created)}",
            f"Total materials: {len(all_materials)}",
            f"Errors: {len(errors)}",
        ]

        if all_materials:
            summary_lines.append("\nMaterials found:")
            for mat in sorted(all_materials):
                summary_lines.append(f"  - {mat}")

        if errors:
            summary_lines.append("\nErrors encountered:")
            for error in errors:
                summary_lines.append(f"  - {error}")

        summary_lines.append("="*60)
        summary = "\n".join(summary_lines)

        print(f"\n{summary}")

        return {
            'success': len(components_created) > 0,
            'components': components_created,
            'assemblies': assemblies_created,
            'materials': all_materials,
            'errors': errors,
            'summary': summary
        }


# Convenience function
def convert_bgeo_to_usd(
    bgeo_folder: str,
    output_folder: str,
    **kwargs
) -> Dict:
    """
    Convert BGEO files to KB3D USD structure.

    Args:
        bgeo_folder: Folder with BGEO.SC files
        output_folder: Output folder for USD files
        **kwargs: Additional arguments for BGEOtoUSDConverter.convert()

    Returns:
        Conversion result dictionary
    """
    converter = BGEOtoUSDConverter()
    return converter.convert(bgeo_folder, output_folder, **kwargs)

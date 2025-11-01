"""
Batch Example - Convert Multiple Materials at Once

This example shows how to batch convert all materials in a texture folder.
The function automatically detects all materials and creates both .mtlx and .usd files.

Usage:
    python batch_example.py
    or from Houdini Python Shell:
    exec(open('/path/to/batch_example.py').read())
"""

from tools.material_tools.TexToMtlx_USD import convert_textures_to_materialx

# Define paths
texture_folder = '/media/tushita/TUSHITA_LINUX_DATA/assets/kb3d_missiontominerva/Textures/png4k'
output_folder = '/tmp/materialx_batch'

# Kit information for USD metadata
kit_info = {
    'kitDisplayName': 'Mission To Minerva Materials',
    'kitId': 'mtm_materials',
    'kitVersion': '1.0.0'
}

print("Scanning texture folder for materials...")
results = convert_textures_to_materialx(
    texture_folder=texture_folder,
    output_folder=output_folder,
    kit_info=kit_info,
    create_usd=True,
    texture_variants=['png4k', 'jpg2k', 'jpg1k'],
    relative_texture_path='../../Textures/'
)

# Print results
print("\n" + "="*60)
print("BATCH CONVERSION RESULTS")
print("="*60)

for result in results:
    status = "✓" if result['success'] else "✗"
    print(f"{status} {result['material']}")

    if result['success']:
        print(f"  MaterialX: {result['materialx_file']}")
        if 'usd_file' in result:
            print(f"  USD: {result['usd_file']}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

print("\n" + "="*60)
print(f"Total materials processed: {len(results)}")
print(f"Successful: {sum(1 for r in results if r['success'])}")
print(f"Failed: {sum(1 for r in results if not r['success'])}")
print("="*60)

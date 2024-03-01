# Imports module metadata to DB (suseAppstream)
# Matches "RPM artifacts" of a module to the existing package entries
# using NEVRA comparison (suseAppstreamPackage)
#
# Usage: <script> channel_id modulemd_file_path

import sys
from uyuni.common.appstreams import ModuleMdImporter

if len(sys.argv) < 3:
  print("Not enough args.")
  sys.exit(1)

channel_id = sys.argv[1]
filename = sys.argv[2]

importer = ModuleMdImporter(channel_id, filename)
importer.import_modules()

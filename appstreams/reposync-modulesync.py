# Imports module metadata to DB (suseModule)
# Matches "RPM artifacts" of a module to the existing package entries
# using NEVRA comparison (suseModulePackage)
#
# Usage: <script> channel_id modulemd_file_path

import re
import sys
import gi
from psycopg2.extensions import AsIs
gi.require_version("Modulemd", "2.0")
from gi.repository import Modulemd

from spacewalk.server import rhnSQL

from spacewalk.server.rhnLib import parseRPMFilename
from spacewalk.satellite_tools.repo_plugins.yum_src import RawSolvablePackage

def parse_rpm_name(nevra):
    # Define a regular expression pattern to extract components
    pattern = re.compile(r'(?P<name>[a-zA-Z0-9._-]+)-'
                         r'(?P<epoch>\d+:)?'
                         r'(?P<version>[a-zA-Z0-9._-]+)-'
                         r'(?P<release>[a-zA-Z0-9._+-]+)\.'
                         r'(?P<arch>[a-zA-Z0-9._-]+)')

    # Match the pattern against the input RPM name
    match = pattern.match(nevra)

    if match:
        # Extract components from the matched groups
        name = match.group('name')
        epoch = match.group('epoch')[:-1] if match.group('epoch') else None  # Remove the trailing ":" if epoch is present
        version = match.group('version')
        release = match.group('release')
        arch = match.group('arch')

        # Return the components as a list
        return [name, epoch, version, release, arch]
    else:
        # Return None if no match is found
        return None


rhnSQL.initDB()

if len(sys.argv) < 3:
  print("Not enough args.")
  sys.exit(1)

channel_id = sys.argv[1]
q_insert_module = rhnSQL.prepare("""INSERT INTO suseModule
                      (SELECT sequence_nextval('suse_as_module_seq'), :chid, ':n', ':s', ':v', ':c', ':a')""")

# Use chnanel ID as well
q_get_pkg_id = rhnSQL.prepare("""SELECT p.id from rhnPackage p WHERE p.name_id = lookup_package_name(':pname')
                        AND p.evr_id = lookup_evr(:epoch, ':version', ':release', 'rpm')
                        AND p.package_arch_id = lookup_package_arch(':parch')""")

q_insert_module_package = rhnSQL.prepare("""INSERT INTO suseModulePackage VALUES (:pid,
                       (SELECT id FROM suseModule WHERE channel_id = :chid
                        AND name = ':n' AND stream = ':s' AND version = ':v' AND context = ':c' AND arch = ':a'))""")


filename = sys.argv[2]
idx = Modulemd.ModuleIndex.new()
idx.update_from_file(filename, True)
no_missing = 0
no_total = 0
for module_name in idx.get_module_names():
  module = idx.get_module(module_name)
  for stream in module.get_all_streams():
    print(f"Processing '{stream.get_NSVCA()}'")
    try:
      q_insert_module.execute(n=AsIs(stream.get_module_name()), s=AsIs(stream.get_stream_name()), v=AsIs(stream.get_version()),
          c=AsIs(stream.get_context()), a=AsIs(stream.get_arch()), chid=channel_id)
    except e:
      print(e)
    for rpm in stream.get_rpm_artifacts():
      if rpm.endswith('.src'):
        # Skip src packages
        continue
      nevra = parse_rpm_name(rpm)
      q_get_pkg_id.execute(pname=AsIs(nevra[0]), parch=AsIs(nevra[4]), epoch=nevra[1] if nevra[1] != '0' else None,
          version=AsIs(nevra[2]), release=AsIs(nevra[3]))
      pid = q_get_pkg_id.fetchone()
      no_total += 1
      if pid:
        pid = pid[0]
        q_insert_module_package.execute(pid=pid, n=AsIs(stream.get_module_name()), s=AsIs(stream.get_stream_name()),
            v=AsIs(stream.get_version()), c=AsIs(stream.get_context()), a=AsIs(stream.get_arch()), chid=channel_id)
        print('.'.join(nevra) + f' is #{pid}')
      else:
        no_missing += 1
        print('.'.join(nevra) + ' is not in the DB')
    print('----')

rhnSQL.commit()
print(f"{no_total - no_missing}/{no_total} packages matched")

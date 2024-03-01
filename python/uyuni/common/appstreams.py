import re
import sys

import gi
gi.require_version("Modulemd", "2.0")
from gi.repository import Modulemd

from spacewalk.server import rhnSQL

class Nevra:
    name: str
    epoch: str = None
    version: str
    release: str
    arch: str

    def __init__(self, name, epoch, version, release, arch):
        self.name = name
        self.epoch = epoch
        self.version = version
        self.release = release
        self.arch = arch

    def __repr__(self):
        epoch_str = f"{self.epoch}:" if self.epoch else ""
        return f"{self.name}-{epoch_str}{self.version}-{self.release}.{self.arch}"

class Nsvca:
    name: str
    stream: str
    version: str
    context: str
    arch: str

    def __init__(self, module):
        self.name = module.get_module_name()
        self.stream = module.get_stream_name()
        self.version = module.get_version()
        self.context = module.get_context()
        self.arch = module.get_arch()

    def __repr__(self):
        return f"{self.name}:{self.stream}:{self.version}:{self.context}:{self.arch}"

class ModuleMdImporter:
    def __init__(self, channel_id, modulemd_file):
        self.channel_id = channel_id
        self.modulemd_file = modulemd_file
        self._index_modulemd()
        rhnSQL.initDB()

    def import_modules(self):
        no_missing = 0
        no_total = 0
        for module in self._get_modules():
            for stream in module.get_all_streams():
                print(f"Processing '{stream.get_NSVCA()}'")
                nsvca = Nsvca(stream)
                module_id = self._insert_module(nsvca)
                if not module_id:
                    continue

                for rpm in stream.get_rpm_artifacts():
                    if rpm.endswith('.src'):
                        # TODO: Skip or not?
                        # Skip source packages
                        continue

                    nevra = self._parse_rpm_name(rpm)
                    no_total += 1

                    pid = self._insert_module_package(nevra, module_id)
                    if pid:
                        print(f"{nevra} is #{pid}")
                    else:
                        no_missing += 1
                        print(f"{nevra} is not in the repository.")

        rhnSQL.commit()
        print(f"{no_total - no_missing}/{no_total} packages matched.")

    def _index_modulemd(self):
        idx = Modulemd.ModuleIndex.new()
        idx.update_from_file(self.modulemd_file, True)
        self.modulemd_index = idx

    def _get_modules(self):
        return [self.modulemd_index.get_module(name) for name in self.modulemd_index.get_module_names()]

    def _insert_module(self, module: Nsvca):
        q_insert_module = rhnSQL.prepare("""
            INSERT INTO suseAppstream (id, channel_id, name, stream, version, context, arch)
            VALUES (sequence_nextval('suse_as_module_seq'), :chid, :n, :s, :v, :c, :a)
            ON CONFLICT (name, stream, version, context, arch) DO UPDATE SET
               name = :n,
               stream = :s,
               version = :v,
               context = :c,
               arch = :a
            RETURNING id
        """)

        q_insert_module.execute(
            chid = self.channel_id,
            n = module.name,
            s = module.stream,
            v = module.version,
            c = module.context,
            a = module.arch
        )

        # Return the newly inserted module ID
        row = q_insert_module.fetchone()
        return row[0] if row else None

    def _insert_module_package(self, pkg: Nevra, module_id: int):
        q_insert_module_pkg = rhnSQL.prepare("""
            INSERT INTO suseAppstreamPackage (package_id, module_id)
                SELECT p.id, :module_id FROM rhnPackage p WHERE p.name_id = lookup_package_name(:pname)
                   AND p.evr_id = lookup_evr(:epoch, :version, :release, 'rpm')
                   AND p.package_arch_id = lookup_package_arch(:parch)
                ON CONFLICT DO NOTHING
                RETURNING package_id
        """)

        q_insert_module_pkg.execute(
            pname = pkg.name,
            epoch = pkg.epoch,
            version = pkg.version,
            release = pkg.release,
            parch = pkg.arch,
            module_id = module_id
        )

        # Return the package ID if exists or None otherwise
        row = q_insert_module_pkg.fetchone()
        return row[0] if row else None

    @staticmethod
    def _parse_rpm_name(nevra):
        pattern = re.compile(r'(?P<name>[a-zA-Z0-9._-]+)-'
                             r'(?P<epoch>\d+:)?'
                             r'(?P<version>[a-zA-Z0-9._-]+)-'
                             r'(?P<release>[a-zA-Z0-9._+-]+)\.'
                             r'(?P<arch>[a-zA-Z0-9._-]+)')

        match = pattern.match(nevra)
        if(match):
            name = match.group('name')
            epoch = match.group('epoch')[:-1] if match.group('epoch') else None # Remove the trailing ':' if epoch is present
            version = match.group('version')
            release = match.group('release')
            arch = match.group('arch')

            # Return the components as a list
            return Nevra(name, epoch, version, release, arch)
        else:
            raise ValueError(f"The value {nevra} cannot be parsed as a NEVRA string.")

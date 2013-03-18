#!/usr/bin/env python
"""
Download and patch the latest version of pytz
"""
import os
import argparse

LATEST_OLSON = "2013b"
#
# TODO: Slurp the latest URL from the pypi downloads page
SRC_TEMPLATE = "https://pypi.python.org/packages/source/p/pytz/pytz-{}.zip"

def download(args):
    "Get the latest pytz"
    import urllib
    source = SRC_TEMPLATE.format(args.olson)
    dest = os.path.basename(source)
    print "Downloading %s" % source

    if os.path.exists(dest):
        print "File %s already exists." % dest
    else:
        urllib.urlretrieve(source, dest)
        print "Download complete."


def compile(args):
    """"Create a 'pytz' directory and create the appengine-compatible module.

    Copy over the bare minimum Python files (pytz/*.py) and put the zonefiles
    into a zip file.
    """
    from zipfile import ZipFile, ZIP_DEFLATED

    source = os.path.basename(SRC_TEMPLATE.format(args.olson))
    build_dir = args.build
    zone_file = os.path.join(build_dir, "zoneinfo.zip")

    print "Recreating pytz for appengine from %s into %s" % (source, build_dir)

    if not os.path.exists(build_dir):
        os.mkdir(build_dir)

    with ZipFile(source, 'r') as zf:

        # copy the source
        for zip_file_obj in (zfi for zfi in zf.filelist if "/pytz/" in
                zfi.filename and zfi.filename.endswith(".py")):

            filename = zip_file_obj.filename # full path in the zip

            out_filename = "%s/%s" % (build_dir,
                    filename[filename.find('/pytz/') + 6:])

            if not os.path.exists(os.path.dirname(out_filename)):
                os.mkdir(os.path.dirname(out_filename))

            with open(out_filename, 'w') as outfile:
                print "Copying %s" % out_filename
                outfile.write(zf.read(zip_file_obj))
        
        # copy the zoneinfo to a new zip file
        with ZipFile(zone_file, "w", ZIP_DEFLATED) as out_zones:
            zonefiles = [zfi for zfi in zf.filelist if "/pytz/zoneinfo" in
                    zfi.filename]
            prefix = os.path.commonprefix([zfi.filename for zfi in zonefiles])
            for zip_file_obj in zonefiles:
                # the destination zip will contain only the contents of the
                # zoneinfo directory e.g.
                # pytz-2013b/pytz/zoneinfo/America/Eastern
                # becoems America/Eastern in our zoneinfo.zip
                out_filename = os.path.relpath(zip_file_obj.filename, prefix)
                print "Writing %s to %s" % (out_filename, zone_file)
                out_zones.writestr(out_filename, zf.read(zip_file_obj))

    print "Files copied from %s to the %s directory" % (source,
            build_dir)




def clean(args):
    """Erase all the compiled and downloaded documents, being
    pytz/*
    pytz-*
    """
    import shutil
    from glob import glob

    print "Removing pytz- and pytz/*"
    for filename in glob("./pytz-*.zip"):
        print "unlink %s" % filename
        os.unlink(filename)

    for dirname in glob("./pytz-*"):
        print "rmtree %s" % dirname
        shutil.rmtree(dirname)

    print "rmtree %s" % args.build
    shutil.rmtree(args.build)




commands = dict(
        download=download,
        compile=compile,
        clean=clean,
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update the pytz.')

    parser.add_argument('--olson', dest='olson', default=LATEST_OLSON,
            help='The version of the pytz to use')

    parser.add_argument('--build', dest='build', default='pytz',
            help='The build directory where the updated pytz will be stored')

    parser.add_argument('command', help='Action to perform',
            choices=commands.keys())

    args = parser.parse_args()

    command = commands[args.command]
    command(args)

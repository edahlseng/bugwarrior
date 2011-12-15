import os
import optparse
import sys

from ConfigParser import ConfigParser

example_bugwarriorrc = """
# Example ~/.bugwarriorrc
#

# General stuff.
[general]
# Here you define a comma separated list of targets.  Each of them must have a
# section below determining their properties, how to query them, etc.  The name
# is just a symbol, and doesn't have any functional importance.
targets = my_github, my_bitbucket, paj_bitbucket, moksha_trac

# The bitly username and api key are used to shorten URLs to the issues for your
# task list.
bitly_api_user = YOUR_USERNAME
bitly_api_key = YOUR_API_KEY

# This is a github example.  It says, "scrape every issue from every repository
# on http://github.com/ralphbean.  It doesn't matter if ralphbean owns the issue
# or not."
[my_github]
service = github
username = ralphbean

# This is the same thing, but for bitbucket.  Each target entry must have a
# 'service' attribute which must be one of 'github', 'bitbucket', or 'trac'.
[my_bitbucket]
service = bitbucket
username = ralphbean

# Here's another bitbucket one.  Here we want to scrape the issues from repos of
# another user, but only include them in the taskwarrior db if they're assigned
# to me.
[paj_bitbucket]
service = bitbucket
username = paj
only_if_assigned = ralphbean

# Here's an example of a trac target.  Scrape every ticket and only include them
# if 1) they're owned by me or 2) they're currently unassigned.
[moksha_trac]
service = trac
url = https://fedorahosted.org/moksha/
only_if_assigned = ralph
also_unassigned = True
"""

# TODO -- get this from bugwarrior.services
SERVICES = ['github', 'bitbucket', 'trac']

def die(msg):
    print "* There was a problem with your ~/.bugwarriorrc"
    print "*  ", msg
    print "* Here's an example template to help:"
    print example_bugwarriorrc
    sys.exit(1)


def parse_args():
    p = optparse.OptionParser()
    p.add_option('-f', '--config', default='~/.bugwarriorrc')
    return p.parse_args()


def validate_config(config):
    if not config.has_section('general'):
        die("No [general] section found.")

    targets = config.get('general', 'targets')
    if not targets:
        die("No targets= item in [general] found.")

    targets = [t.strip() for t in targets.split(",")]

    if set(targets + ["general"]) != set(config.sections()):
        die("List of targets and list of sections don't match.")

    for option in ['bitly.api_user', 'bitly.api_key']:
        if not config.has_option('general', option):
            die("[general] is missing '%s'" % option)

    # Define some section-specific validators
    # TODO -- maybe pull this from bugwarrior.services
    def _validate_github(config, target):
        if not config.has_option(target, 'username'):
            die("[%s] has no 'username'" % target)
        # TODO -- validate other options

    def _validate_bitbucket(config, target):
        if not config.has_option(target, 'username'):
            die("[%s] has no 'username'" % target)
        # TODO -- validate other options

    def _validate_trac(config, target):
        if not config.has_option(target, 'url'):
            die("[%s] has no 'url'" % target)
        # TODO -- validate other options

    validate_section = {
        'github': _validate_github,
        'bitbucket': _validate_bitbucket,
        'trac': _validate_trac,
    }

    # Validate each target one by one.
    for target in targets:
        service = config.get(target, 'service')
        if not service:
            die("No 'service' in [%s]" % target)

        if service not in SERVICES:
            die("'%s' in [%s] is not a valid service." % (service, target))

        # Call the service-specific validator
        validate_section[service](config, target)


def load_config():
    opts, args = parse_args()

    config = ConfigParser()
    config.read(os.path.expanduser(opts.config))

    validate_config(config)

    return config
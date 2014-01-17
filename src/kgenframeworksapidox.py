#! /usr/bin/env python

# Python 2/3 compatibility (NB: we require at least 2.7)
from __future__ import division, absolute_import, print_function, unicode_literals

import argparse, os, shutil, sys

scriptdir = os.path.dirname(os.path.realpath(__file__))
import kgenapidox

def get_tier(yaml_file):
    """Parse the tier out of a yaml file"""
    with open(yaml_file) as f:
        import yaml
        data = yaml.load(f)
        return data['tier']

def generate_group_menu(tiers):
    """Generate a menu for the frameworks"""
    sections = []
    for t in range(1,5):
        frameworks = []
        for fw in tiers[t]:
            rellink = '../../' + fw['outputdir'] + '/html/index.html'
            frameworks.append({
                'href': rellink,
                'name': fw['fancyname']
                })
        sections.append({
            'title': 'Tier ' + str(t),
            'members': frameworks
            })
    return {'group_title': 'Frameworks', 'sections': sections}

def process_toplevel_html_file(inputfile, outputfile, tiers, title,
        api_searchbox=False):
    """Pass a HTML file through the templating filters"""

    frameworks = {}
    gm_sections = []
    for t in range(1,5):
        gm_frameworks = []
        for fw in tiers[t]:
            rellink = fw['outputdir'] + '/html/index.html'
            gm_frameworks.append({
                'href': rellink,
                'name': fw['fancyname']
                })
            frameworks[fw['framework']] = {'link': rellink, 'name': fw['fancyname']}
        gm_sections.append({
            'title': 'Tier ' + str(t),
            'members': gm_frameworks
            })
    group_menu = {'group_title': 'Frameworks', 'sections': gm_sections}

    mapping = {
            'resources': '.',
            'api_searchbox': api_searchbox,
            # steal the doxygen css from one of the frameworks
            # this means that all the doxygen-provided images etc. will be found
            'doxygencss': tiers[1][0]['outputdir'] + '/html/doxygen.css',
            'title': title,
            'breadcrumbs': {
                'entries': [
                    {
                        'href': 'http://api.kde.org/',
                        'text': 'KDE API Reference'
                    }
                    ]
                },
            'group_menu': group_menu,
            'frameworks': frameworks
        }
    import pystache
    renderer = pystache.Renderer(decode_errors='ignore')
    with open(outputfile, 'w') as outf:
        outf.write(renderer.render_path(inputfile, mapping))

def main():
    parser = argparse.ArgumentParser(description='Generate API documentation ' +
            'for the KDE Frameworks')
    parser.add_argument('frameworksdir',
            help='Location of the frameworks modules.')
    parser.add_argument('--title', default='KDE API Documentation',
            help='String to use for page titles.')
    parser.add_argument('--man-pages', action='store_true',
            help='Generate man page documentation.')
    parser.add_argument('--qhp', action='store_true',
            help='Generate Qt Compressed Help documentation.')
    parser.add_argument('--searchengine', action='store_true',
            help="Enable Doxygen's search engine feature.")
    parser.add_argument('--api-searchbox', action='store_true',
            help="Enable the API searchbox (only useful for api.kde.org).")
    parser.add_argument('--no-apidocs-suffix', action='store_false',
            dest='use_suffix',
            help='Call the apidocs folders "<framework>" instead of ' +
                 '"<framework>-apidocs".')
    parser.add_argument('--doxdatadir',
            help='Location of the HTML header files and support graphics.')
    parser.add_argument('--qtdoc-dir',
            help='Location of (local) Qt documentation; this is searched ' +
                 'for tag files to create links to Qt classes.')
    parser.add_argument('--qtdoc-link',
            help='Override Qt documentation location for the links in the ' +
                 'html files.  May be a path or URL.')
    parser.add_argument('--qtdoc-flatten-links', action='store_true',
            help='Whether to assume all Qt documentation html files ' +
                 'are immediately under QTDOC_LINK (useful if you set ' +
                 'QTDOC_LINK to the online Qt documentation).  Ignored ' +
                 'if QTDOC_LINK is not set.')
    parser.add_argument('--doxygen', default='doxygen',
            help='(Path to) the doxygen executable.')
    parser.add_argument('--qhelpgenerator', default='qhelpgenerator',
            help='(Path to) the qhelpgenerator executable.')
    args = parser.parse_args()

    doxdatadir = kgenapidox.find_doxdatadir_or_exit(args.doxdatadir)
    tagfiles = kgenapidox.search_for_tagfiles(
            suggestion = args.qtdoc_dir,
            doclink = args.qtdoc_link,
            flattenlinks = args.qtdoc_flatten_links,
            searchpaths = ['/usr/share/doc/qt5', '/usr/share/doc/qt'])

    if not os.path.isdir(args.frameworksdir):
        print(args.frameworksdir + " is not a directory")
        exit(2)

    framework_list = os.listdir(args.frameworksdir)
    tiers = {1:[],2:[],3:[],4:[]}
    for framework in framework_list:
        fwdir = os.path.join(args.frameworksdir, framework)
        outputdir = framework
        if args.use_suffix:
            outputdir += '-apidocs'
        readme_file = os.path.join(fwdir, 'README.md')
        yaml_file = os.path.join(fwdir, framework + '.yaml')
        if not os.path.isfile(readme_file) or not os.path.isfile(yaml_file):
            print(framework + " is not a framework (README.md or " +
                 framework + ".yaml missing)")
        else:
            # FIXME: option in yaml file to disable docs
            fancyname = kgenapidox.parse_fancyname(readme_file, default=framework)
            tier = get_tier(yaml_file)
            if tier is None:
                print("Could not find tier for " + framework + "!")
            elif tier < 1 or tier > 4:
                print("Invalid tier " + tier + " for " + framework + "!")
            else:
                tiers[tier].append({
                    'framework': framework,
                    'fancyname': fancyname,
                    'srcdir': fwdir,
                    'outputdir': outputdir
                    })

    for t in range(1,5):
        tiers[t] = sorted(tiers[t], key=lambda f: f['fancyname'].lower())

    kgenapidox.copy_dir_contents(os.path.join(doxdatadir,'htmlresource'),'.')

    group_menu = generate_group_menu(tiers)

    def gen_fw_apidocs(fwinfo, rebuild=False):
        kgenapidox.generate_apidocs(
                modulename = fwinfo['framework'],
                fancyname = fwinfo['fancyname'],
                srcdir = fwinfo['srcdir'],
                outputdir = fwinfo['outputdir'],
                doxdatadir = doxdatadir,
                tagfiles = tagfiles,
                man_pages = args.man_pages,
                qhp = args.qhp,
                searchengine = args.searchengine,
                api_searchbox = args.api_searchbox,
                doxygen = args.doxygen,
                qhelpgenerator = args.qhelpgenerator,
                title = args.title,
                resourcedir = '../..',
                template_mapping = {
                    'breadcrumbs': {
                        'entries': [
                            {
                                'href': 'http://api.kde.org/',
                                'text': 'KDE API Reference'
                            },
                            {
                                'href': '../../index.html',
                                'text': 'Frameworks'
                            }
                            ]
                        },
                    'group_menu': group_menu
                    },
                doxyfile_entries = { 'WARN_IF_UNDOCUMENTED': True }
                )
        if not rebuild:
            tagfile = os.path.abspath(
                        os.path.join(
                            fwinfo['outputdir'],
                            'html',
                            fwinfo['framework']+'.tags'))
            tagfiles.append((tagfile,'../../' + fwinfo['outputdir'] + '/html/'))

    process_toplevel_html_file(os.path.join(doxdatadir, 'frameworks.html'), 'index.html',
            title=args.title, tiers=tiers, api_searchbox=args.api_searchbox)

    for t in range(1,5):
        for fwinfo in tiers[t]:
            gen_fw_apidocs(fwinfo)
        if (t >= 3):
            # Rebuild for interdependencies
            # FIXME: can we be cleverer about deps?
            for fwinfo in tiers[t]:
                shutil.rmtree(fwinfo['outputdir'])
                gen_fw_apidocs(fwinfo, rebuild=True)


if __name__ == "__main__":
    main()


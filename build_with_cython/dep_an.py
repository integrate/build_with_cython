import os
from modulegraph import find_modules

def _get_deps_list(ref_list, package_source, ignore_names):
    package_name = os.path.split(package_source)[1]
    res = []
    for dep in ref_list:
        #only include source modules
        if dep.__class__.__name__!="SourceModule":
            continue

        #only include from this package
        mod_source_path = dep.filename
        mod_package_source_path = os.path.split(mod_source_path)[0]

        if mod_package_source_path!=package_source:
            continue

        name = dep.identifier.lstrip(package_name+".")
        # ignore
        if name in ignore_names:
            continue

        res.append(name)

    return res

def get_dep_list(package_source):
    package_source = os.path.abspath(package_source)

    # no init py - no modules will be accessible
    init_py_path = os.path.join(package_source, "__init__.py")
    if not os.path.isfile(init_py_path):
        return []

    package_name = os.path.split(package_source)[1]

    #get deps of root module
    modgraph = find_modules.find_modules(packages=[package_name])
    root_refs = modgraph.getReferences(None)
    peps_struct=[] #{name:"", deps=[]}

    res = _get_deps_list(root_refs, package_source, [])
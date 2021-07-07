import os
from modulegraph import find_modules


def remove_package_name(fullname, packagename):
    packagename+="."
    l = len(packagename)
    if fullname[0:l] == packagename:
        return fullname[l: len(fullname)]

    return fullname

def _get_deps_list(ref_list, package_source, ignore_names):
    package_name = os.path.split(package_source)[1]
    res = []
    for dep in ref_list:
        # only include source modules
        if dep.__class__.__name__ != "SourceModule":
            continue

        # only include from this package
        mod_source_path = dep.filename
        mod_package_source_path = os.path.split(mod_source_path)[0]

        if mod_package_source_path != package_source:
            continue


        name = remove_package_name(dep.identifier, package_name)
        # ignore
        if name in ignore_names:
            continue

        res.append(name)

    return res


def _tree_to_list(tree):
    mod_list = []
    while len(tree) != 0:
        len_before = len(tree)

        # sort by count of dependencies
        def el_to_key(el):
            return len(el['deps'])

        tree.sort(key=el_to_key)

        # add empty els to result
        mods = []
        for el in tree:
            if len(el['deps']) == 0:
                mods.append(el['name'])

        # remove added mods from list and from dependencies
        for mod in mods:
            for el in tree.copy():
                if el['name'] == mod:  # remove added modules
                    tree.remove(el)
                elif mod in el['deps']:  # remove added dependencies
                    el['deps'].remove(mod)

        # check that amount become less
        len_after = len(tree)
        if len_before <= len_after:
            raise Exception("build_with_cython: Can't make module list!")

        mod_list += mods

    return  mod_list

def _dep_tree_contains_mod(mod_name, dep_tree):
    for el in dep_tree:
        if el['name'] == mod_name:
            return True
    return False

def _add_mod_dep_tree(modgraph, package_source, mod_name, dep_tree):
    if _dep_tree_contains_mod(mod_name, dep_tree):
        return

    package_name = os.path.split(package_source)[1]

    refs = modgraph.getReferences(package_name + "." + mod_name)
    deps = _get_deps_list(refs, package_source, [])
    dep_tree.append({"name": mod_name, "deps": deps})
    for depmod in deps:
        _add_mod_dep_tree(modgraph, package_source, depmod, dep_tree)


def get_dep_list(package_source, full_module_list):
    package_source = os.path.abspath(package_source)

    # no init py - no modules will be accessible
    init_py_path = os.path.join(package_source, "__init__.py")
    if not os.path.isfile(init_py_path):
        return []

    package_name = os.path.split(package_source)[1]

    # get deps of root module
    modgraph = find_modules.find_modules(packages=[package_name])
    # modgraph.create_xref()
    root_refs = modgraph.getReferences(package_name)

    # get tree
    all_modules = full_module_list.copy()#_get_deps_list(root_refs, package_source, [])
    deps_struct = []  # {name:"", deps=[]}
    for mod in all_modules:
        _add_mod_dep_tree(modgraph, package_source, mod, deps_struct)

    # tree to list
    return _tree_to_list(deps_struct)

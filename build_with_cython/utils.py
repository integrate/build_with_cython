import sys, os, shutil, stat, setuptools


def remove_folder(path):
    def handleRemoveReadonly(func, path, exc):
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)

    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=handleRemoveReadonly)


def get_files_from_folder_by_ext(path, ext, add_path=True, add_name=True, add_ext=True):
    if not hasattr(ext, "__iter__"):
        ext = [ext]

    res = []
    for [p, dirs, files] in os.walk(path):
        for f in files:
            name, ex = os.path.splitext(f)
            if ex in ext:

                # make result
                r = ""
                if add_name: r += name
                if add_ext: r += ex
                if add_path:
                    if len(r) > 0:
                        r = os.path.join(p, r)
                    else:
                        r = p

                res.append(r)

    return res


def copy_python_files(src, dst):
    def ign(path, content):
        ignore = []
        for f in content:
            ff = os.path.join(path, f)
            if os.path.isdir(ff) and f[0] == ".":
                ignore.append(f)
            if os.path.isdir(ff) and f in ["venv", "__pycache__"]:
                ignore.append(f)
            elif os.path.isfile(ff) and os.path.splitext(f)[1] != ".py":
                ignore.append(f)

        return ignore

    shutil.copytree(src, dst, ignore=ign)


def prepare_init_py_file(package_source_path):
    init_py_path = os.path.join(package_source_path, "__init__.py")
    init_pyx_path = os.path.join(package_source_path, "__init__.pyx")

    # if __init__.pyx is here - nothing to do
    if os.path.isfile(init_pyx_path):
        return init_pyx_path

    # if __init__.py is here - it will be renamed
    if os.path.isfile(init_py_path):
        os.replace(init_py_path, init_pyx_path)
        return init_pyx_path

    # create new __init__.pyx file
    f = open(init_pyx_path, "w+")
    f.close()
    return init_pyx_path


def generate_module_loading_code(module_name):
    return """
cdef extern from *:
    \"\"\"
    PyObject *PyInit_""" + module_name + """(void);
    \"\"\"
    object PyInit_""" + module_name + """()
    
PyImport_AppendInittab(\"""" + module_name + """\", PyInit_""" + module_name + """)
sys.builtin_module_names = list(sys.builtin_module_names)+[\"""" + module_name + """\"]
"""


def generate_modules_loading_code(module_names):
    res = """
###### AUTO GENERATED CODE ### BEGIN ######
import sys
cdef extern from "Python.h":
    int PyImport_AppendInittab(const char *name, object (*initfunc)())
"""
    for m in module_names:
        res += generate_module_loading_code(m)

    res += """
###### AUTO GENERATED CODE ### END ######

"""

    return res


def patch_pyx_file_to_load_modules(pyx_file, module_names):
    if "__init__" in module_names:
        module_names.remove("__init__")

    add_str = generate_modules_loading_code(module_names)

    with open(pyx_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(add_str + content)


def clean_temp_build_files(**kwargs):
    # clean temp files
    setuptools.setup(script_args=["--quiet", "clean", "--all", ], **kwargs)


def build_ext(result_path, **kwargs):
    try:
        # prepare params
        result_path_param = '--dist-dir=' + result_path
        temp_path_param = "--dist-dir=build"

        include_dirs = ";".join([sys.prefix, sys.exec_prefix])

        setuptools.setup(script_args=["bdist_wheel", result_path_param, temp_path_param], **kwargs)
    except:
        return False

    return True

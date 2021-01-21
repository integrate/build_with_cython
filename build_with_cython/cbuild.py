from wheel.bdist_wheel import bdist_wheel as _base_command

from Cython.Build import cythonize

import os, shutil

BUILD_TEMP = "cbuild_temp"


class CBuild(_base_command):
    description = 'convert all ext_modules to c and makes wheel with binary extension'

    def remove_python_files(self, list):
        for f in list:
            try:
                if os.path.isfile(f) and os.path.splitext(f)[1] == ".py":
                    os.unlink(f)
            except:
                pass

    def remove_folder(self, path):
        def handleRemoveReadonly(func, path, exc):
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
            func(path)

        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=False, onerror=handleRemoveReadonly)

    def make_folder(self, path, make_empty=False):
        if os.path.isdir(path) and make_empty:
            self.remove_folder(path)

        try:
            os.makedirs(path)
        except OSError:
            print("Creation of the directory %s failed" % path)

    def copy_python_files(self, src, dst):
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

    def copy_to_temp_folder(self, list):
        new_sources = []
        for f in list:
            path, name = os.path.split(f)

            new_path = os.path.join(BUILD_TEMP, path)
            self.make_folder(new_path)

            new_file = os.path.join(new_path, name)
            shutil.copy(f, new_file)
            new_sources.append(new_file)

        return new_sources

    def prepare_init_py_file(self, package_source_path, sources_list):
        init_py_path = os.path.join(package_source_path, "__init__.py")
        init_pyx_path = os.path.join(package_source_path, "__init__.pyx")

        # if __init__.pyx is here - nothing to do
        if os.path.isfile(init_pyx_path):
            return init_pyx_path

        # if __init__.py is here - it will be renamed
        if os.path.isfile(init_py_path):
            os.replace(init_py_path, init_pyx_path)

            if init_py_path in sources_list:
                sources_list.remove(init_py_path)
            sources_list.append(init_pyx_path)

            return init_pyx_path

        # create new __init__.pyx file
        f = open(init_pyx_path, "w+")
        f.close()

        sources_list.append(init_pyx_path)

        return init_pyx_path

    def get_files_from_folder_by_ext(self, path, ext, add_path=True, add_name=True, add_ext=True):
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

    def generate_module_loading_code(self, module_name):
        return """
cdef extern from *:
    \"\"\"
    PyObject *PyInit_""" + module_name + """(void);
    \"\"\"
    object PyInit_""" + module_name + """()

PyImport_AppendInittab(\"""" + module_name + """\", PyInit_""" + module_name + """)
sys.builtin_module_names = list(sys.builtin_module_names)+[\"""" + module_name + """\"]
"""

    def generate_modules_loading_code(self, module_names):
        res = """
###### AUTO GENERATED CODE ### BEGIN ######
import sys
cdef extern from "Python.h":
    int PyImport_AppendInittab(const char *name, object (*initfunc)())
"""
        for m in module_names:
            res += self.generate_module_loading_code(m)

        res += """
###### AUTO GENERATED CODE ### END ######

"""

        return res

    def patch_pyx_file_to_load_modules(self, pyx_file, module_names):
        if "__init__" in module_names:
            module_names.remove("__init__")

        add_str = self.generate_modules_loading_code(module_names)

        with open(pyx_file, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(add_str + content)

    def run(self):

        # prepare temp folder
        self.make_folder(BUILD_TEMP, True)

        # copy to temp folder
        for ext in self.distribution.ext_modules:
            new_sources = self.copy_to_temp_folder(ext.sources)
            ext.sources = new_sources

            #prepare __init__
            package_source =  os.path.split(ext.sources[0])[0]
                # make sure there is __init__.pyx in the root of package
            init_pyx_path = self.prepare_init_py_file(package_source, ext.sources)
            module_names = self.get_files_from_folder_by_ext(package_source, [".py", ".pyx"], False, True, False)
            self.patch_pyx_file_to_load_modules(init_pyx_path, module_names)


        # generate c files
        orig_modules = self.distribution.ext_modules
        self.distribution.ext_modules = cythonize(self.distribution.ext_modules, language_level=3, force=True)

        # remove python files
        for ext in orig_modules:
            self.remove_python_files(ext.sources)

        # run original command
        res = super().run()

        # remove temp folder
        self.remove_folder(BUILD_TEMP)

        return res
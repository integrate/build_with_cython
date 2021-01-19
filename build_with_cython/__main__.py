import git, utils, os, setuptools, shutil
from Cython.Build import cythonize

import settings

# create dir with sources
if settings.REBUILD_FROM_SOURCES:

    if os.path.isdir(settings.SOURCE_PATH):
        utils.remove_folder(settings.SOURCE_PATH)

    if settings.SOURCE_FLAG == 'repo':
        git.Repo.clone_from(settings.REPO_URL, settings.SOURCE_PATH, multi_options=["--branch " + settings.REPO_BRANCH])
    elif settings.SOURCE_FLAG == "folder":
        utils.copy_python_files(settings.REPO_FOLDER, settings.SOURCE_PATH)

    else:
        print("unknown source flag!!!")
        exit()

    #make sure there is __init__.pyx in the root of package
    init_pyx_path = utils.prepare_init_py_file(settings.SOURCE_PATH)
    module_names = utils.get_files_from_folder_by_ext(settings.SOURCE_PATH, [".py", ".pyx"], False, True, False)
    utils.patch_pyx_file_to_load_modules(init_pyx_path, module_names)

# make C files
if settings.REBUILD_C_FILES:
    c_source_list = utils.get_files_from_folder_by_ext(settings.SOURCE_PATH, [".py", ".pyx"])
    ext = [setuptools.extension.Extension(settings.EXT_NAME, c_source_list)]
    ext_c = cythonize(ext, language_level=3, force=True)
else:
    c_source_list = utils.get_files_from_folder_by_ext(settings.SOURCE_PATH, ".c")
    ext_c = [setuptools.extension.Extension(settings.EXT_NAME, c_source_list)]

# general setup settings
setup_args = {
    # distribution name
    "name": settings.DISTRIBUTION_NAME,
    "version": settings.DISTRIBUTION_VER,

    "ext_package": settings.TOP_PACKAGE_NAME,
    "ext_modules": ext_c
}

# build extension
if settings.REBUILD_EXTENSION:
    # clean before rebuild
    if settings.REBUILD_EXTENSION_FORCE:
        utils.clean_temp_build_files(**setup_args)  # temp files
        utils.remove_folder(settings.RESULT_PATH)  # results of previous builds

    suc = utils.build_ext(settings.RESULT_PATH, **setup_args)
    if suc:
        print("")
        print("SUCCESS")
    else:
        print("")
        print("FAILED")

# remove temp files
if settings.REMOVE_TEMP_BUILD_FILES_AFTER:
    utils.clean_temp_build_files(**setup_args)

# remove source files
if settings.REMOVE_SOURCE_FILES_AFTER:
    utils.remove_folder(settings.SOURCE_PATH)

# apply new lib
# ex = ".pyd"
# sign = "cp38-win_amd64"
# lib = settings.EXT_NAME + ex
# if os.path.isfile(lib):
#     os.unlink(lib)
#
# src = os.path.join(settings.RESULT_PATH, settings.TOP_PACKAGE_NAME, settings.EXT_NAME + "." + sign + ex)
# dst = settings.EXT_NAME + ex
# shutil.copy(src, dst)
# print("Copied from", src, "to", dst)

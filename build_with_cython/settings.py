EXT_NAME = 'pygame_wrap1'
# библиотека pyd будет с этим именем. И ее уже нельзя будет переименовать.

TOP_PACKAGE_NAME = "pygame_engine"
#будет создана папка с этим именем, в которую и положат созданную библиотеку .pyd
#   и другие, если они будут

DISTRIBUTION_NAME = "pygame_engine"
#имя wheel файла и проекта в каталогах
DISTRIBUTION_VER = "0.1.0"

SOURCE_FLAG='repo' # folder/repo
REPO_URL = "https://github.com/integrate/pygame_wrap1"
REPO_BRANCH = "ver_0_1_0"
REPO_FOLDER = "C:\\Users\\vmatv\\PycharmProjects\\pygame_wrap1"

SOURCE_PATH = "temp_src/"+EXT_NAME #конечная папка должна совпадать с именем EXT_NAME. Иначе будет ошибка при сборке.
RESULT_PATH = "build_result" #downloaded version of repo


#build phases
REBUILD_FROM_SOURCES = True
REBUILD_C_FILES = True

REBUILD_EXTENSION = True
REBUILD_EXTENSION_FORCE = True

REMOVE_TEMP_BUILD_FILES_AFTER = False

REMOVE_SOURCE_FILES_AFTER = False
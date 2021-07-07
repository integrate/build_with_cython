set base_dir=%~dp0..
set ver=0.0.3

set twine=%base_dir%\venv\scripts\twine.exe
set ver_name=%base_dir%\dist\build_with_cython-0.0.3-py3-none-any.whl

IF EXIST %ver_name% (%twine% upload %ver_name%)

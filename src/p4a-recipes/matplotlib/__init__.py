from pythonforandroid.toolchain import PythonRecipe

class MatplotlibImageRecipe(PythonRecipe):
    version = '2.2.2'
    url = 'https://github.com/matplotlib/matplotlib/archive/v{version}.zip'

    depends = ['python2', 'setuptools']

    site_packages_name = 'matplotlib'

    call_hostpython_via_targetpython = False

recipe = MatplotlibImageRecipe()
